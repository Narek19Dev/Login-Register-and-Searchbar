const $ = (sel) => document.querySelector(sel);

function setStatus(text, isError = false) {
  const el = $('#status');
  el.textContent = text || '';
  el.style.color = isError ? '#ff9898' : '#9acbff';
}

let progressTimer = null;

function pollProgress()() {
  try {
    const res = window.pyBridge.get_progress();
    if (res && typeof res.progress === 'number') {
      const pct = Math.max(0, Math.min(100, res.progress|0));
      $('#progressBar').style.width = pct + '%';
    }
    if (res && res.status) setStatus(res.status);
  } catch {}
}

function loadConfig() {
  try {
    const cfg = window.pyBridge ? window.pyBridge.get_config() : null;
    if (!cfg) return;
    $('#nickname').value = cfg.nickname || '';
    $('#sborkaUrl').value = cfg.sborka_url || '';
    $('#winePath').value = cfg.wine_path || '';
    $('#sampRel').value = cfg.samp_relative_path || 'samp.exe';
  } catch (e) {
    setStatus('Failed to load config: ' + e.message, true);
  }
}

function saveConfig() {
  const config = {
    nickname: $('#nickname').value.trim(),
    sborka_url: $('#sborkaUrl').value.trim(),
    wine_path: $('#winePath').value.trim(),
    samp_relative_path: $('#sampRel').value.trim() || 'samp.exe',
  };
  try {
    const res = window.pyBridge.save_config(JSON.stringify(config));
    if (res && res.ok) setStatus('Saved');
    else setStatus('Save failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
  } catch (e) {
    setStatus('Save failed: ' + e.message, true);
  }
}

function downloadSborka() {
  try {
    const res = window.pyBridge.download_sborka();
    if (res && res.ok) {
      setStatus('Starting download…');
      if (progressTimer) clearInterval(progressTimer);
      progressTimer = setInterval(pollProgress, 500);
    } else {
      setStatus('Download failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
    }
  } catch (e) {
    setStatus('Download failed: ' + e.message, true);
  }
}

function launch() {
  const nick = $('#nickname').value.trim();
  if (!nick) return setStatus('Enter nickname', true);
  try {
    const res = window.pyBridge.launch(nick);
    if (res && res.ok) setStatus('Launching…');
    else setStatus('Launch failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
  } catch (e) {
    setStatus('Launch failed: ' + e.message, true);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  $('#save').addEventListener('click', saveConfig);
  $('#download').addEventListener('click', downloadSborka);
  $('#launch').addEventListener('click', launch);
  loadConfig();
  pollProgress();
});