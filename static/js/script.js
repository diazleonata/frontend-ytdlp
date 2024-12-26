async function download() {
    const url = document.getElementById('url').value;
    const status = document.getElementById('status');

    if (!url) {
        alert('Please enter a URL!');
        return;
    }

    status.textContent = 'Downloading...';

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to download');
        }

        // Extract the filename from the Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1].replace(/"/g, '') // Extract filename safely
            : 'video.mp4'; // Default fallback

        // Convert the response to a blob and download it
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();

        status.textContent = 'Download complete!';
    } catch (error) {
        console.error(error);
        status.textContent = `Error: ${error.message}`;
    }
}
