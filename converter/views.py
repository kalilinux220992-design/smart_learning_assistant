import re
import subprocess
import tempfile
from pathlib import Path

from django.http import FileResponse
from django.shortcuts import render
from django.utils.text import slugify
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from yt_dlp import YoutubeDL

from .forms import YouTubePDFForm

MAX_SCREENSHOTS = 500


def parse_timestamp(value):
    value = value.strip()
    parts = value.split(':')
    if len(parts) > 3:
        raise ValueError('Use HH:MM:SS or MM:SS format')

    total_seconds = 0
    for index, part in enumerate(reversed(parts)):
        if not part.isdigit():
            raise ValueError('Timestamp must contain only numbers and colons')
        total_seconds += int(part) * (60 ** index)

    return total_seconds


def parse_interval(value):
    value = value.strip()
    if not value:
        raise ValueError('Interval is required')
    if ':' in value:
        return parse_timestamp(value)
    if not value.isdigit():
        raise ValueError('Interval must be a positive integer or HH:MM:SS')

    interval_seconds = int(value)
    if interval_seconds <= 0:
        raise ValueError('Interval must be greater than zero')

    return interval_seconds


def get_video_duration(video_path):
    command = [
        'ffprobe',
        '-v',
        'error',
        '-show_entries',
        'format=duration',
        '-of',
        'default=noprint_wrappers=1:nokey=1',
        str(video_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        duration_text = result.stdout.strip()
        if duration_text and duration_text != 'N/A':
            try:
                return float(duration_text)
            except ValueError:
                pass

    ffmpeg_result = subprocess.run(
        ['ffmpeg', '-i', str(video_path), '-f', 'null', '-'],
        capture_output=True,
        text=True,
        stderr=subprocess.STDOUT,
    )
    match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)', ffmpeg_result.stdout or '')
    if match:
        hours, minutes, seconds = match.groups()
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)

    raise ValueError('Could not determine the video duration from the provided file.')


def resolve_video_path(video_url, local_video_path, destination_dir):
    if local_video_path:
        candidate = Path(local_video_path).expanduser().resolve()
        if candidate.exists() and candidate.is_file():
            return candidate
        raise FileNotFoundError(f'The local video file was not found: {candidate}')

    if not video_url:
        raise ValueError('Please provide either a YouTube URL or a local video path.')

    return download_video(video_url, destination_dir)


def download_video(video_url, destination_dir):
    output_template = str(destination_dir / 'video.%(ext)s')
    options = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
    }

    with YoutubeDL(options) as ydl:
        ydl.extract_info(video_url, download=True)

    candidates = [
        destination_dir / 'video.mp4',
        destination_dir / 'video.webm',
        destination_dir / 'video.mkv',
        destination_dir / 'video.mov',
        destination_dir / 'video.avi',
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError('The video could not be downloaded')


def create_frame(video_path, timestamp, output_path):
    command = [
        'ffmpeg',
        '-y',
        '-ss',
        str(timestamp),
        '-i',
        str(video_path),
        '-frames:v',
        '1',
        '-q:v',
        '2',
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def compute_image_hash(image, hash_size=8):
    resample = getattr(Image, 'Resampling', Image).LANCZOS
    image = image.convert('L').resize((hash_size, hash_size), resample)
    pixels = list(image.getdata())

    hash_bits = 0
    for pixel in pixels:
        hash_bits = (hash_bits << 1) | (1 if pixel > 128 else 0)

    return hash_bits


def hamming_distance(hash1, hash2):
    return bin(hash1 ^ hash2).count('1')


def is_different_enough(previous_hash, current_hash, min_uniqueness):
    if min_uniqueness <= 0:
        return True

    max_bits = 8 * 8
    diff = hamming_distance(previous_hash, current_hash)
    uniqueness = diff / max_bits
    return uniqueness >= (min_uniqueness / 100)


def create_frames(video_path, interval_seconds, output_dir, min_uniqueness=0, max_frames=MAX_SCREENSHOTS):
    duration = get_video_duration(video_path)
    timestamps = []
    current_time = 0
    while current_time <= duration:
        timestamps.append(current_time)
        current_time += interval_seconds
    if not timestamps:
        raise ValueError('No frames could be captured from this video.')
    if len(timestamps) > max_frames:
        raise ValueError(
            f'The requested interval would produce too many screenshots ({len(timestamps)}). '
            'Use a larger interval, a shorter video, or reduce the number of screenshots.'
        )

    image_paths = []
    last_hash = None
    for index, timestamp in enumerate(timestamps, start=1):
        image_path = output_dir / f'frame_{index:03d}.jpg'
        create_frame(video_path, timestamp, image_path)

        if min_uniqueness > 0:
            with Image.open(image_path) as image:
                current_hash = compute_image_hash(image)

            if last_hash is None or is_different_enough(last_hash, current_hash, min_uniqueness):
                last_hash = current_hash
                image_paths.append((timestamp, image_path))
            else:
                image_path.unlink(missing_ok=True)
        else:
            image_paths.append((timestamp, image_path))

    return image_paths


def create_pdf(image_paths, output_pdf, title):
    pdf_width, pdf_height = letter
    canvas_obj = canvas.Canvas(str(output_pdf), pagesize=letter)
    canvas_obj.setTitle(title)
    for page_index, (timestamp, image_path) in enumerate(image_paths, start=1):
        if page_index > 1:
            canvas_obj.showPage()

        image = Image.open(image_path).convert('RGB')
        width, height = image.size
        scale = min(pdf_width / width, pdf_height / height)
        scaled_width = width * scale
        scaled_height = height * scale

        canvas_obj.setFont('Helvetica-Bold', 14)
        canvas_obj.drawString(40, 750, f'{title} — {timestamp:.0f}s')
        canvas_obj.drawString(40, 730, f'Page {page_index} of {len(image_paths)}')
        canvas_obj.drawImage(
            ImageReader(image),
            (pdf_width - scaled_width) / 2,
            (pdf_height - scaled_height) / 2,
            width=scaled_width,
            height=scaled_height,
            preserveAspectRatio=True,
        )
    canvas_obj.save()


def index(request):
    form = YouTubePDFForm()
    error_message = None

    if request.method == 'POST':
        form = YouTubePDFForm(request.POST)
        if form.is_valid():
            video_url = form.cleaned_data.get('video_url') or ''
            local_video_path = form.cleaned_data.get('local_video_path') or ''
            interval_value = form.cleaned_data['interval']
            try:
                interval_seconds = parse_interval(interval_value)
                min_uniqueness = form.cleaned_data.get('min_uniqueness') or 0
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    video_path = resolve_video_path(video_url, local_video_path, temp_path)
                    frames_dir = temp_path / 'frames'
                    frames_dir.mkdir()
                    image_paths = create_frames(video_path, interval_seconds, frames_dir, min_uniqueness=min_uniqueness)
                    pdf_path = temp_path / 'screenshots.pdf'
                    title = f'YouTube screenshots every {interval_seconds}s'
                    create_pdf(image_paths, pdf_path, title)

                    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
                    filename = f'{slugify(title)}.pdf'
                    response['Content-Disposition'] = f'attachment; filename={filename}'
                    return response
            except Exception as exc:
                error_message = f'Could not create the PDF: {exc}'
        else:
            error_message = 'Please provide a valid YouTube URL and screenshot interval.'

    return render(request, 'converter/index.html', {'form': form, 'error_message': error_message})
