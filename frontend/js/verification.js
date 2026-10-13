/**
 * ====================================================================
 * GREENLOOPAI — REAL WASTE VERIFICATION CONTROLLER
 * Connects frontend image upload to real backend verification pipeline:
 * Detect → Verify → Reward
 * ====================================================================
 */

(function (window) {
  'use strict';

  const Verification = {
    currentFile: null,
    currentObjectUrl: null,
    maxSizeBytes: 10 * 1024 * 1024, // 10 MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'],
    isProcessing: false,

    init() {
      this.initDropzone();
      this.initFileInput();
      this.initActionButtons();
    },

    initDropzone() {
      const dropzone = document.getElementById('upload-dropzone');
      const fileInput = document.getElementById('waste-file-input');

      if (!dropzone || !fileInput) return;

      ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add('drag-active');
        }, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove('drag-active');
        }, false);
      });

      dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
          this.handleFile(files[0]);
        }
      });

      dropzone.addEventListener('click', () => {
        fileInput.click();
      });
    },

    initFileInput() {
      const fileInput = document.getElementById('waste-file-input');
      if (!fileInput) return;

      fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
          this.handleFile(fileInput.files[0]);
        }
      });
    },

    handleFile(file) {
      if (!file) return;

      if (!this.allowedTypes.includes(file.type.toLowerCase())) {
        if (window.App && window.App.showToast) {
          window.App.showToast('Invalid File', 'Please upload a supported image format (JPG, PNG, or WEBP).', 'danger');
        }
        return;
      }

      if (file.size > this.maxSizeBytes) {
        if (window.App && window.App.showToast) {
          window.App.showToast('File Too Large', 'Maximum allowed file size is 10 MB.', 'danger');
        }
        return;
      }

      this.currentFile = file;

      if (this.currentObjectUrl) {
        URL.revokeObjectURL(this.currentObjectUrl);
      }

      this.currentObjectUrl = URL.createObjectURL(file);
      this.renderPreview(file, this.currentObjectUrl);
    },

    renderPreview(file, objectUrl) {
      const dropzone = document.getElementById('upload-dropzone');
      const previewCard = document.getElementById('upload-preview-card');
      const previewImg = document.getElementById('preview-image-element');
      const fileNameEl = document.getElementById('preview-file-name');
      const fileSizeEl = document.getElementById('preview-file-size');
      const fileTypeEl = document.getElementById('preview-file-type');

      if (dropzone) dropzone.style.display = 'none';
      if (previewCard) previewCard.classList.add('active');

      if (previewImg) previewImg.src = objectUrl;
      if (fileNameEl) fileNameEl.textContent = file.name;
      if (fileSizeEl) fileSizeEl.textContent = this.formatFileSize(file.size);
      if (fileTypeEl) fileTypeEl.textContent = file.type || 'image/jpeg';

      const statusBox = previewCard ? previewCard.querySelector('.service-status-box') : null;
      if (statusBox) {
        const isLive = window.GreenLoopAPI && window.GreenLoopAPI.isConnected;
        const span = statusBox.querySelector('span');
        if (span) {
          if (isLive) {
            span.textContent = 'AI Backend connected. Ready for real YOLOv8 detection, OCR, and verification scoring.';
            statusBox.classList.add('status-box-connected');
          } else {
            span.textContent = 'Verification service is not connected. Connect the verification backend to process this image.';
            statusBox.classList.remove('status-box-connected');
          }
        }
      }

      if (window.App && window.App.showToast) {
        window.App.showToast('Image Loaded', 'Ready for multi-modal waste verification.', 'info');
      }
    },

    removeFile() {
      if (this.currentObjectUrl) {
        URL.revokeObjectURL(this.currentObjectUrl);
        this.currentObjectUrl = null;
      }
      this.currentFile = null;

      const fileInput = document.getElementById('waste-file-input');
      if (fileInput) fileInput.value = '';

      const dropzone = document.getElementById('upload-dropzone');
      const previewCard = document.getElementById('upload-preview-card');
      const previewImg = document.getElementById('preview-image-element');

      if (previewImg) previewImg.src = '';
      if (previewCard) previewCard.classList.remove('active');
      if (dropzone) dropzone.style.display = 'flex';
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    initActionButtons() {
      const removeBtn = document.getElementById('btn-remove-image');
      if (removeBtn) {
        removeBtn.addEventListener('click', () => this.removeFile());
      }

      const changeBtn = document.getElementById('btn-change-image');
      const fileInput = document.getElementById('waste-file-input');
      if (changeBtn && fileInput) {
        changeBtn.addEventListener('click', () => fileInput.click());
      }

      const verifyBtn = document.getElementById('btn-start-verification');
      if (verifyBtn) {
        verifyBtn.addEventListener('click', () => this.triggerVerification());
      }
    },

    /**
     * Executes REAL verification via backend API.
     */
    async triggerVerification() {
      if (!this.currentFile) {
        if (window.App && window.App.showToast) {
          window.App.showToast('No Image', 'Select a waste image before continuing.', 'warning');
        }
        return;
      }

      if (this.isProcessing) return;

      const verifyBtn = document.getElementById('btn-start-verification');
      const originalText = verifyBtn ? verifyBtn.innerHTML : 'Start Verification';

      try {
        this.isProcessing = true;
        if (verifyBtn) {
          verifyBtn.disabled = true;
          verifyBtn.innerHTML = `<span>Processing Verification...</span>`;
        }

        if (window.App && window.App.showToast) {
          window.App.showToast('Processing', 'Running Vision, OCR, and Authenticity checks...', 'info', 4000);
        }

        const result = await window.GreenLoopAPI.verifyWasteImage(this.currentFile);

        // Store active verified result in memory for UI presentation and context-aware assistant
        window.GreenLoopActiveResult = result;

        this.populateVerificationResult(result);

        if (window.App && window.App.showToast) {
          window.App.showToast(
            result.verified ? 'Verification Complete' : 'Verification Incomplete',
            `Score: ${result.verification_score}% | GreenCoins: +${result.reward.greencoins_awarded}`,
            result.verified ? 'success' : 'warning'
          );
        }

        // Allow user to see live stage card diagnostics light up, then transition to full result view
        setTimeout(() => {
          if (window.Navigation) {
            if (typeof window.Navigation.switchView === 'function') {
              window.Navigation.switchView('result');
            } else if (typeof window.Navigation.navigateTo === 'function') {
              window.Navigation.navigateTo('result');
            }
          }
        }, 1200);

      } catch (err) {
        let errorMsg = 'AI processing service unavailable.';
        if (err.data && err.data.message) {
          errorMsg = err.data.message;
        } else if (err.message) {
          errorMsg = err.message;
        }

        if (window.App && window.App.showToast) {
          window.App.showToast('Verification Notice', errorMsg, 'danger', 6000);
        }

        // If backend offline, show informative system modal
        if (err.name === 'TypeError' || err.status === 503) {
          if (window.App && window.App.openModal) {
            window.App.openModal('modal-backend-notice');
          }
        }
      } finally {
        this.isProcessing = false;
        if (verifyBtn) {
          verifyBtn.disabled = false;
          verifyBtn.innerHTML = originalText;
        }
      }
    },

    populateVerificationResult(result) {
      // 1. Update Inline Diagnostics on "Verify Waste" Screen
      const scoreDisplayVal = document.getElementById('score-display-value');
      const scoreDisplayStatus = document.getElementById('score-display-status');
      const scoreCircle = document.getElementById('score-gauge-circle');

      if (scoreDisplayVal) scoreDisplayVal.textContent = Math.round(result.verification_score);
      if (scoreDisplayStatus) {
        scoreDisplayStatus.textContent = result.verified ? 'Verification Passed (Live AI)' : result.status;
        scoreDisplayStatus.style.color = result.verified ? '#4D8F2A' : '#D97706';
      }
      if (scoreCircle) {
        const radius = 70;
        const circumference = 2 * Math.PI * radius;
        scoreCircle.style.strokeDasharray = `${circumference}`;
        const offset = circumference - (result.verification_score / 100) * circumference;
        scoreCircle.style.strokeDashoffset = `${offset}`;
        scoreCircle.style.stroke = result.verified ? '#66B539' : (result.verification_score > 40 ? '#F59E0B' : '#EF4444');
      }

      // Stage 1: Waste Detection
      const diagCategory = document.getElementById('diag-waste-category');
      const diagConfidence = document.getElementById('diag-waste-confidence');
      const diagWasteStatus = document.getElementById('diag-waste-status');
      const topObj = result.detected_objects && result.detected_objects.length > 0 ? result.detected_objects[0] : null;

      if (diagCategory) diagCategory.textContent = topObj ? topObj.category : 'None Detected';
      if (diagConfidence) diagConfidence.textContent = topObj ? `${(topObj.confidence * 100).toFixed(1)}%` : '0.0%';
      if (diagWasteStatus) {
        diagWasteStatus.textContent = topObj ? `Detected (${topObj.label})` : 'No waste object recognized';
        diagWasteStatus.className = `badge ${topObj ? 'badge-success' : 'badge-warning'}`;
      }

      // Stage 2: Brand Verification
      const diagBrand = document.getElementById('diag-brand-name');
      const diagBrandMatch = document.getElementById('diag-brand-match');
      const diagBrandStatus = document.getElementById('diag-brand-status');

      if (diagBrand) diagBrand.textContent = result.brand_detection.brand || 'Unbranded / Not Detected';
      if (diagBrandMatch) diagBrandMatch.textContent = result.brand_detection.confidence ? `${(result.brand_detection.confidence * 100).toFixed(0)}% Match` : 'N/A';
      if (diagBrandStatus) {
        diagBrandStatus.textContent = result.brand_detection.brand ? 'Brand Recognized' : 'Generic / No Brand';
        diagBrandStatus.className = `badge ${result.brand_detection.brand ? 'badge-success' : 'badge-neutral'}`;
      }

      // Stage 3: Authenticity
      const diagAuthScore = document.getElementById('diag-auth-score');
      const diagAuthMeta = document.getElementById('diag-auth-metadata');
      const diagAuthStatus = document.getElementById('diag-auth-status');

      if (diagAuthScore) diagAuthScore.textContent = `${(result.authenticity.score * 100).toFixed(0)}%`;
      if (diagAuthMeta) diagAuthMeta.textContent = result.authenticity.exif_present ? `${result.authenticity.camera_make || 'Device'} Hardware Metadata` : 'Standard Screen / Web Capture';
      if (diagAuthStatus) {
        diagAuthStatus.textContent = result.authenticity.exif_present ? 'Physical Camera Verified' : 'Standard Web Image';
        diagAuthStatus.className = `badge ${result.authenticity.exif_present ? 'badge-success' : 'badge-neutral'}`;
      }

      // Stage 4: Reward Yield
      const diagRewardCoins = document.getElementById('diag-reward-coins');
      const diagRewardTier = document.getElementById('diag-reward-tier');
      const diagRewardStatus = document.getElementById('diag-reward-status');

      if (diagRewardCoins) diagRewardCoins.textContent = `+${result.reward.greencoins_awarded} GC`;
      if (diagRewardTier) diagRewardTier.textContent = result.reward.reward_tier || 'NONE';
      if (diagRewardStatus) {
        diagRewardStatus.textContent = result.reward.greencoins_awarded > 0 ? 'Tokens Allocated' : 'No Reward Granted';
        diagRewardStatus.className = `badge ${result.reward.greencoins_awarded > 0 ? 'badge-success' : 'badge-neutral'}`;
      }

      // 2. Update Full Detailed Verification Result View
      const resScoreVal = document.getElementById('res-score-value');
      const resScoreStatus = document.getElementById('res-score-status');
      const resScoreCircle = document.getElementById('res-score-circle');
      const resScoreBadge = document.getElementById('res-score-badge');
      const resRewardCoins = document.getElementById('res-reward-coins');

      if (resScoreVal) resScoreVal.textContent = Math.round(result.verification_score);
      if (resScoreStatus) {
        resScoreStatus.textContent = result.verified ? 'Verification Passed (Live AI)' : result.status;
        resScoreStatus.style.color = result.verified ? '#4D8F2A' : '#D97706';
      }
      if (resScoreBadge) {
        resScoreBadge.textContent = result.verified ? 'VERIFIED' : 'UNVERIFIED';
        resScoreBadge.className = `badge ${result.verified ? 'badge-success' : 'badge-warning'}`;
      }
      if (resScoreCircle) {
        const radius = 70;
        const circumference = 2 * Math.PI * radius;
        resScoreCircle.style.strokeDasharray = `${circumference}`;
        const offset = circumference - (result.verification_score / 100) * circumference;
        resScoreCircle.style.strokeDashoffset = `${offset}`;
        resScoreCircle.style.stroke = result.verified ? '#66B539' : (result.verification_score > 40 ? '#F59E0B' : '#EF4444');
      }

      if (resRewardCoins) resRewardCoins.textContent = `+${result.reward.greencoins_awarded} GC`;

      const resWasteCategory = document.getElementById('res-waste-category');
      const resWasteConfidence = document.getElementById('res-waste-confidence');
      const resWasteStatus = document.getElementById('res-waste-status');

      if (resWasteCategory) resWasteCategory.textContent = topObj ? topObj.category : 'None Detected';
      if (resWasteConfidence) resWasteConfidence.textContent = topObj ? `${(topObj.confidence * 100).toFixed(1)}%` : '0.0%';
      if (resWasteStatus) {
        resWasteStatus.textContent = topObj ? `Detected (${topObj.label})` : 'No waste object recognized';
        resWasteStatus.className = `badge ${topObj ? 'badge-success' : 'badge-warning'}`;
      }

      const resBrandName = document.getElementById('res-brand-name');
      const resBrandMatch = document.getElementById('res-brand-match');
      const resBrandStatus = document.getElementById('res-brand-status');

      if (resBrandName) resBrandName.textContent = result.brand_detection.brand || 'Unbranded / Not Detected';
      if (resBrandMatch) resBrandMatch.textContent = result.brand_detection.confidence ? `${(result.brand_detection.confidence * 100).toFixed(0)}% Match` : 'N/A';
      if (resBrandStatus) {
        resBrandStatus.textContent = result.brand_detection.brand ? 'Brand Recognized' : 'Generic / No Brand';
        resBrandStatus.className = `badge ${result.brand_detection.brand ? 'badge-success' : 'badge-neutral'}`;
      }

      const resAuthScore = document.getElementById('res-auth-score');
      const resAuthMeta = document.getElementById('res-auth-metadata');
      const resAuthStatus = document.getElementById('res-auth-status');

      if (resAuthScore) resAuthScore.textContent = `${(result.authenticity.score * 100).toFixed(0)}%`;
      if (resAuthMeta) resAuthMeta.textContent = result.authenticity.exif_present ? `${result.authenticity.camera_make || 'Device'} Hardware Metadata` : 'Standard Screen / Web Capture';
      if (resAuthStatus) {
        resAuthStatus.textContent = result.authenticity.exif_present ? 'Physical Camera Verified' : 'Standard Web Image';
        resAuthStatus.className = `badge ${result.authenticity.exif_present ? 'badge-success' : 'badge-neutral'}`;
      }

      // Stage: How to Recycle This Guidance Link
      const resRecycleCategory = document.getElementById('res-recycle-category-name');
      const resRecycleStatus = document.getElementById('res-recycle-status-badge');
      const resRecycleSummary = document.getElementById('res-recycle-summary-text');
      const btnRecycleGuide = document.getElementById('btn-open-result-recycle-guide');

      const detectedWaste = topObj ? (topObj.category || topObj.label || 'plastic_bottle') : 'general_waste';
      const detectedConfidence = topObj ? topObj.confidence : 0.85;

      if (resRecycleCategory) resRecycleCategory.textContent = topObj ? topObj.category : 'General Waste';
      if (resRecycleStatus) {
        resRecycleStatus.textContent = result.verified ? 'Recycling Guidance Ready' : 'Inspection Complete';
        resRecycleStatus.className = 'badge badge-success';
      }
      if (resRecycleSummary) {
        resRecycleSummary.textContent = `Get verified preparation instructions, decontamination rules, and safe disposal routes for ${topObj ? topObj.category : 'this waste item'}.`;
      }

      if (btnRecycleGuide) {
        btnRecycleGuide.disabled = false;
        btnRecycleGuide.onclick = () => {
          if (window.GreenLoopRecycling && window.GreenLoopRecycling.openGuideForWaste) {
            window.GreenLoopRecycling.openGuideForWaste(detectedWaste, detectedConfidence);
          }
        };
      }
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    Verification.init();
  });

  window.Verification = Verification;

})(window);
