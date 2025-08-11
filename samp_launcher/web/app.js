const $ = (sel) => document.querySelector(sel);

function setStatus(text, isError = false) {
  const el = $('#status');
  el.textContent = text || '';
  el.style.color = isError ? '#ff9898' : '#9acbff';
}

function loadConfig() {
  try {
    const cfg = window.pyBridge ? window.pyBridge.get_config() : null;
    if (!cfg) return;
    $('#server').value = cfg.server_ip_port || '';
    $('#nickname').value = cfg.nickname || '';
    $('#password').value = cfg.password || '';
    $('#skinUrl').value = cfg.skin_download_url || '';
  } catch (e) {
    setStatus('Failed to load config: ' + e.message, true);
  }
}

function saveConfig() {
  const config = {
    server_ip_port: $('#server').value.trim(),
    nickname: $('#nickname').value.trim(),
    password: $('#password').value,
    skin_download_url: $('#skinUrl').value.trim(),
  };
  try {
    const res = window.pyBridge.save_config(JSON.stringify(config));
    if (res && res.ok) setStatus('Saved');
    else setStatus('Save failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
  } catch (e) {
    setStatus('Save failed: ' + e.message, true);
  }
}

function downloadSkin() {
  const nick = $('#nickname').value.trim();
  if (!nick) return setStatus('Enter nickname to download skin', true);
  try {
    const res = window.pyBridge.download_skin(nick);
    if (res && res.ok) {
      const img = $('#skinImg');
      img.src = res.path;
      $('#skinPreview').classList.remove('hidden');
      setStatus('Skin downloaded');
    } else {
      setStatus('Download failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
    }
  } catch (e) {
    setStatus('Download failed: ' + e.message, true);
  }
}

function connect() {
  const server = $('#server').value.trim();
  const nick = $('#nickname').value.trim();
  const pass = $('#password').value;
  if (!server) return setStatus('Enter server ip:port', true);
  if (!nick) return setStatus('Enter nickname', true);
  try {
    const res = window.pyBridge.connect(server, nick, pass);
    if (res && res.ok) setStatus('Opening SA:MP…');
    else setStatus('Connect failed: ' + (res && res.error ? res.error : 'Unknown error'), true);
  } catch (e) {
    setStatus('Connect failed: ' + e.message, true);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  $('#save').addEventListener('click', saveConfig);
  $('#downloadSkin').addEventListener('click', downloadSkin);
  $('#connect').addEventListener('click', connect);
  loadConfig();
});