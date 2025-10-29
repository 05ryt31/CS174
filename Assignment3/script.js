// Function to fetch and display trucking companies using server-side processing
async function loadTruckingCompanies() {
  const inputEl = document.getElementById('jsonUrl');
  const errorEl = document.getElementById('errorMessage');
  clearError();

  const filename = (inputEl?.value || '').trim();
  if (!filename) {
    setError('Please enter a valid JSON filename');
    return;
  }

  try {
    // Send filename to Python CGI script for server-side processing
    const serverUrl = `/cgi-bin/process_json.py?file=${encodeURIComponent(filename)}`;
    const res = await fetch(serverUrl, { cache: 'no-store' });
    
    if (!res.ok) {
      throw new Error('NETWORK_NOT_OK');
    }

    const htmlContent = await res.text();
    
    // Open popup with the HTML content returned from server
    openPopupWithHTML(htmlContent);
    
  } catch (err) {
    if (String(err.message) === 'NETWORK_NOT_OK') {
      setError('Error: Network response was not ok.');
    } else {
      setError('Error: Could not connect to server.');
      console.error(err);
    }
  }

  function clearError() {
    if (errorEl) {
      errorEl.textContent = '';
    }
  }
  function setError(msg) {
    if (errorEl) {
      errorEl.textContent = msg;
    } else {
      alert(msg);
    }
  }
}

// Open popup with HTML content from server
function openPopupWithHTML(htmlContent) {
  const win = window.open('', '_blank', 'width=900,height=650,scrollbars=yes,noopener');
  
  if (!win) {
    // Fallback if popup is blocked
    const fallback = document.getElementById('popupFallback') || document.createElement('div');
    fallback.id = 'popupFallback';
    fallback.innerHTML = htmlContent;
    document.body.appendChild(fallback);
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) errorEl.textContent = 'Popup was blocked — showing content inline.';
    return;
  }
  
  win.document.open();
  win.document.write(htmlContent);
  win.document.close();
}

