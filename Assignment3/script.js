// Function to fetch and display trucking companies
async function loadTruckingCompanies() {
  const inputEl = document.getElementById('jsonUrl');
  const errorEl = document.getElementById('errorMessage');
  clearError();

  const url = (inputEl?.value || '').trim();
  if (!url) {
    setError('Please enter a valid JSON file URL');
    return;
  }

  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) {
      throw new Error('NETWORK_NOT_OK');
    }

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      setError('Invalid JSON file.');
      return;
    }

    const rows = data?.Mainline?.Table?.Row;
    if (!Array.isArray(rows) || rows.length === 0) {
      openPopupWithMessage('No trucking companies found in the JSON file.');
      return;
    }

    const headers =
      Array.isArray(data?.Mainline?.Table?.Header?.Data) &&
      data.Mainline.Table.Header.Data.length
        ? data.Mainline.Table.Header.Data
        : [
            'Parent Company',
            'Subsidiary Portfolio / Services',
            'HQ / Info',
            'Annual Revenue ($ million)',
            'HomePage',
            'Logo'
          ];

    // generate table HTML
    const baseHref = new URL(url, window.location.href).href;
    const tableHTML = buildTableHTML(headers, rows, baseHref);

    openPopupWithTable(tableHTML, baseHref);
  } catch (err) {
    if (String(err.message) === 'NETWORK_NOT_OK') {
      setError('Error: Network response was not ok.');
    } else {
      setError('Error: Network response was not ok.');
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

// Build safe HTML table string from rows
function buildTableHTML(headers, rows, baseHref) {
  const escapeHTML = (s) =>
    String(s ?? '').replace(/[&<>\"']/g, (ch) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch])
    );

  const toAbs = (maybeUrl) => {
    if (!maybeUrl) return '';
    try {
      return new URL(String(maybeUrl), baseHref).href;
    } catch {
      return String(maybeUrl);
    }
  };

  const thead =
    '<thead><tr>' +
    headers.map((h) => `<th>${escapeHTML(h)}</th>`).join('') +
    '</tr></thead>';

  const tbody =
    '<tbody>' +
    rows
      .map((company) => {
        const name = escapeHTML(company?.Company ?? '');
        const services = escapeHTML(company?.Services ?? '');
        const hubsArr = Array.isArray(company?.Hubs?.Hub) ? company.Hubs.Hub : [];
        const hubsHTML = hubsArr.map((h) => escapeHTML(h)).join('<br>');
        const revenue = escapeHTML(company?.Revenue ?? '');

        const homepage = String(company?.HomePage ?? '');
        const homepageAbs = toAbs(homepage);
        const homepageCell = homepage
          ? `<a href="${escapeHTML(homepageAbs)}" target="_blank" rel="noopener">HomePage</a>`
          : '';

        const logo = String(company?.Logo ?? '');
        const logoAbs = toAbs(logo);
        const logoCell = logo
          ? `<img src="${escapeHTML(logoAbs)}" alt="${name ? name + ' Logo' : 'Logo'}" width="50" height="50" />`
          : '';

        return `<tr>
          <td>${name}</td>
          <td>${services}</td>
          <td>${hubsHTML}</td>
          <td>${revenue}</td>
          <td>${homepageCell}</td>
          <td>${logoCell}</td>
        </tr>`;
      })
      .join('') +
    '</tbody>';

  return `<table border="1">${thead}${tbody}</table>`;
}

// Open popup with full HTML document; fallback to inline if blocked (optional)
function openPopupWithTable(tableHTML, baseHref) {
  const win = window.open('', '_blank', 'width=900,height=650,scrollbars=yes,noopener');
  const docHTML = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Trucking Companies</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <base href="${baseHref}">
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 24px; }
    h1 { font-size: 1.25rem; margin: 0 0 12px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
    th { background: #f3f4f6; }
    img { object-fit: contain; }
    a { word-break: break-all; }
  </style>
</head>
<body>
  <h1>Trucking Companies</h1>
  ${tableHTML}
</body>
</html>`;

  if (!win) {
    const fallback = document.getElementById('popupFallback') || document.createElement('div');
    fallback.id = 'popupFallback';
    fallback.innerHTML = '<h2>Trucking Companies</h2>' + tableHTML;
    document.body.appendChild(fallback);
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) errorEl.textContent = 'Popup was blocked — showing table inline.';
    return;
  }
  win.document.open();
  win.document.write(docHTML);
  win.document.close();
}

// Show single-line message in popup (for "No data" case)
function openPopupWithMessage(message) {
  const win = window.open('', '_blank', 'width=600,height=400,scrollbars=yes,noopener');
  const docHTML = `<!doctype html>
<html><head><meta charset="utf-8"><title>Trucking Companies</title></head>
<body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 24px;">
  <p><strong>${String(message).replace(/[&<>\"']/g, (ch) => (
    { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[ch]
  ))}</strong></p>
</body></html>`;
  if (!win) {
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) errorEl.textContent = message;
    else alert(message);
    return;
  }
  win.document.open();
  win.document.write(docHTML);
  win.document.close();
}
