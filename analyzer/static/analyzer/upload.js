const fileUploadInput = document.getElementById('fileupload');
const uploadProgress = document.getElementById('upload-progress');
const uploadPercentage = document.getElementById('upload-percentage');


fileUploadInput.addEventListener('change', (e) => {
  const file = e.target.files[0];

  if (file) {
    const formData = new FormData();
    formData.append('file', file);

    // Simulate file upload progress (for demonstration)
    simulateUploadProgress(formData, file.size);
  }
});

function simulateUploadProgress(formData, fileSize) {
  let progress = 0;
  let uploadedBytes = 0;

  const interval = setInterval(() => {
    if (progress < 100) {
      const chunkSize = fileSize / 20; // Simulate 10 equal parts
      uploadedBytes += chunkSize;
      progress = (uploadedBytes / fileSize) * 100;

      uploadProgress.value = progress;
      uploadPercentage.textContent = progress.toFixed(2) + '%';
      uploadSize.textContent = (uploadedBytes / (1024 * 1024)).toFixed(2) + ' MB';
    } else {
      uploadProgress.value = 100;
      uploadPercentage.textContent = 'Upload Complete';
      clearInterval(interval);
    }
  }, 1000);
}

function handleUploadFailure() {
    uploadPercentage.textContent = 'Upload Failed';
    // You can add further error handling logic here, e.g., displaying an error message to the user.
}

  
