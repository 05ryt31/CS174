// Global variables
let currentTicker = '';

// DOM elements
const searchForm = document.getElementById('search-form');
const tickerInput = document.getElementById('ticker-input');
const searchBtn = document.getElementById('search-btn');
const clearBtn = document.getElementById('clear-btn');
const resultsSection = document.getElementById('results-section');
const errorMessage = document.getElementById('error-message');
const loading = document.getElementById('loading');
const cacheMessage = document.getElementById('cache-message');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    searchForm.addEventListener('submit', handleSearch);
    clearBtn.addEventListener('click', handleClear);
});

// Handle form submission
async function handleSearch(event) {
    event.preventDefault();
    
    const ticker = tickerInput.value.trim();
    
    if (!ticker) {
        alert('Please fill out this field');
        return;
    }
    
    currentTicker = ticker.toUpperCase();
    
    // Show loading, hide other sections
    showLoading();
    hideError();
    hideResults();
    hideCacheMessage();
    
    try {
        const response = await fetch(`/search?ticker=${encodeURIComponent(ticker)}`);
        const data = await response.json();
        
        hideLoading();
        
        if (data.error) {
            showError(`Error: ${data.error}`);
            return;
        }
        
        // Check for cache status
        const cacheStatus = response.headers.get('X-Cache');
        if (cacheStatus === 'HIT') {
            showCacheMessage('Data served from cache');
        }
        
        displayResults(data);
        
    } catch (error) {
        hideLoading();
        showError(`Error: ${error.message}`);
    }
}

// Handle clear button
function handleClear() {
    tickerInput.value = '';
    currentTicker = '';
    hideResults();
    hideError();
    hideCacheMessage();
    tickerInput.focus();
}

// Display search results
function displayResults(data) {
    if (data.company) {
        populateCompanyTable(data.company);
    }
    
    if (data.stock) {
        populateStockTable(data.stock);
    }
    
    showResults();
}

// Populate company outlook table
function populateCompanyTable(companyData) {
    const tableBody = document.querySelector('#company-table tbody');
    
    // Truncate description to 5 lines
    let description = companyData.description || 'N/A';
    const lines = description.split('\n');
    if (lines.length > 5) {
        description = lines.slice(0, 5).join('\n') + '...';
    }
    
    tableBody.innerHTML = `
        <tr><td><strong>Company Name</strong></td><td>${companyData.name || 'N/A'}</td></tr>
        <tr><td><strong>Ticker Symbol</strong></td><td>${companyData.ticker || currentTicker}</td></tr>
        <tr><td><strong>Exchange Code</strong></td><td>${companyData.exchangeCode || 'N/A'}</td></tr>
        <tr><td><strong>Start Date</strong></td><td>${companyData.startDate || 'N/A'}</td></tr>
        <tr><td><strong>Description</strong></td><td>${description}</td></tr>
    `;
}

// Populate stock summary table
function populateStockTable(stockData) {
    const tableBody = document.querySelector('#stock-table tbody');
    
    // Calculate values
    const ticker = stockData.ticker || currentTicker;
    const tradingDay = stockData.timestamp ? new Date(stockData.timestamp).toISOString().split('T')[0] : 'N/A';
    const prevClose = stockData.prevClose || 0;
    const open = stockData.open || 0;
    const high = stockData.high || 0;
    const low = stockData.low || 0;
    const last = stockData.last !== null ? stockData.last : (stockData.tngoLast || 0);
    const volume = stockData.volume || 0;
    
    // Calculate change and change percentage
    const change = last - prevClose;
    const changePercent = prevClose !== 0 ? (change / prevClose) * 100 : 0;
    
    // Format change with arrow
    const changeArrow = change > 0 ? '▲' : '▼';
    const changeClass = change > 0 ? 'positive' : 'negative';
    const changeText = `${change.toFixed(2)} (${changePercent.toFixed(2)}%)`;
    
    tableBody.innerHTML = `
        <tr><td><strong>Ticker Symbol</strong></td><td>${ticker}</td></tr>
        <tr><td><strong>Trading Day</strong></td><td>${tradingDay}</td></tr>
        <tr><td><strong>Previous Closing Price</strong></td><td>$${prevClose.toFixed(2)}</td></tr>
        <tr><td><strong>Opening Price</strong></td><td>$${open.toFixed(2)}</td></tr>
        <tr><td><strong>High Price</strong></td><td>$${high.toFixed(2)}</td></tr>
        <tr><td><strong>Low Price</strong></td><td>$${low.toFixed(2)}</td></tr>
        <tr><td><strong>Last Price</strong></td><td>$${last.toFixed(2)}</td></tr>
        <tr><td><strong>Change</strong></td><td class="${changeClass}">${changeArrow} ${changeText}</td></tr>
        <tr><td><strong>Number of Shares Traded</strong></td><td>${volume.toLocaleString()}</td></tr>
    `;
}

// Load and display search history
async function loadSearchHistory() {
    try {
        const response = await fetch('/history');
        const history = await response.json();
        
        const tableBody = document.querySelector('#history-table tbody');
        
        if (history.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="2">No search history available</td></tr>';
            return;
        }
        
        tableBody.innerHTML = history.map(item => {
            const timestamp = new Date(item.timestamp).toLocaleString();
            return `<tr><td>${item.ticker}</td><td>${timestamp}</td></tr>`;
        }).join('');
        
    } catch (error) {
        console.error('Error loading search history:', error);
        const tableBody = document.querySelector('#history-table tbody');
        tableBody.innerHTML = '<tr><td colspan="2">Error loading search history</td></tr>';
    }
}

// Tab functionality
function openTab(evt, tabName) {
    // Hide all tab content
    const tabContent = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.remove('active');
    }
    
    // Remove active class from all tab buttons
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove('active');
    }
    
    // Show the selected tab and mark button as active
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
    
    // Load history when history tab is clicked
    if (tabName === 'history-tab') {
        loadSearchHistory();
    }
}

// Utility functions for showing/hiding elements
function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showResults() {
    resultsSection.style.display = 'block';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showCacheMessage(message) {
    cacheMessage.textContent = message;
    cacheMessage.style.display = 'block';
}

function hideCacheMessage() {
    cacheMessage.style.display = 'none';
}