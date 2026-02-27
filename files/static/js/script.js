/**
 * Main JavaScript functionality for Internship Matching Platform
 */

// Utility function to format score into badge class
function getScoreBadgeClass(score) {
    if (score >= 85) return 'score-excellent';
    if (score >= 70) return 'score-good';
    if (score >= 50) return 'score-fair';
    return 'score-poor';
}

// Parse URL parameters
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Load and display match results
async function loadResults() {
    const projectId = getUrlParameter('project');
    
    if (!projectId) {
        document.body.innerHTML = '<div class="container"><div class="card" style="margin-top: 40px;"><div class="card-body"><p>❌ No project specified. <a href="/">Go back to home</a></p></div></div></div>';
        return;
    }

    try {
        const response = await fetch(`/match/${projectId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load results');
        }

        displayResults(data);
    } catch (error) {
        console.error('Error loading results:', error);
        document.getElementById('resultsContainer').innerHTML = `
            <div class="card">
                <div class="card-body">
                    <p>❌ Error loading results: ${error.message}</p>
                    <p><a href="/" class="btn btn-secondary">Go back to home</a></p>
                </div>
            </div>
        `;
    }
}

function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const project = data.project;
    const results = data.results;

    let html = `
        <div class="results-section">
            <div class="results-header">
                <h2>${project.role_title} at ${project.company_name}</h2>
                <p><strong>Duration:</strong> ${project.duration}</p>
                ${project.stipend_amount > 0 ? `<p><strong>Stipend:</strong> ₹${project.stipend_amount}/month</p>` : '<p><strong>Stipend:</strong> Not offered</p>'}
                <p><strong>Total Candidates Matched:</strong> ${results.length}</p>
            </div>

            <div class="fairness-notice">
                ⚖️ <strong>Fairness Commitment:</strong> Rankings are based solely on skill competency, experience, and project requirements. No personal demographic information influences the ranking.
            </div>
    `;

    if (results.length === 0) {
        html += `
            <div class="card">
                <div class="card-body">
                    <p>No candidates have been registered yet.</p>
                </div>
            </div>
        `;
    } else {
        html += `
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Candidate Name</th>
                        <th>Experience (months)</th>
                        <th>Availability</th>
                        <th>Match Score</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
        `;

        results.forEach((result, index) => {
            const scoreClass = getScoreBadgeClass(result.match_score);
            html += `
                <tr>
                    <td><strong>${index + 1}</strong></td>
                    <td>${result.candidate_name}</td>
                    <td>${result.experience_months}</td>
                    <td>${result.availability}</td>
                    <td>
                        <span class="score-badge ${scoreClass}">
                            ${result.match_score}%
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-small" onclick="toggleExplanation('exp-${result.candidate_id}')">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr id="exp-${result.candidate_id}" style="display: none;">
                    <td colspan="6">
                        <div class="explanation-section">
                            <div class="explanation-content show">
                                ${formatExplanationContent(result)}
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;
    }

    html += `
            <div style="margin-top: 30px;">
                <a href="/" class="btn btn-secondary">← Back to Home</a>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function formatExplanationContent(result) {
    let html = `
        <div>
            <p><strong>Explanation:</strong> ${result.explanation}</p>
            
            <div style="margin-top: 15px;">
    `;

    if (result.strong_matches && result.strong_matches.length > 0) {
        html += `
            <div style="margin-bottom: 15px;">
                <strong style="color: #22543d;">✓ Strong Matches:</strong>
                <ul class="skill-list">
        `;
        result.strong_matches.forEach(match => {
            const level = ['', 'Beginner', 'Intermediate', 'Advanced'][match.candidate_level];
            html += `<li class="strong-match">${match.skill} (${level})</li>`;
        });
        html += `</ul></div>`;
    }

    if (result.partial_matches && result.partial_matches.length > 0) {
        html += `
            <div style="margin-bottom: 15px;">
                <strong style="color: #7c2d12;">◐ Partial Matches:</strong>
                <ul class="skill-list">
        `;
        result.partial_matches.forEach(match => {
            const candidateLevel = ['', 'Beginner', 'Intermediate', 'Advanced'][match.candidate_level];
            const requiredLevel = ['', 'Beginner', 'Intermediate', 'Advanced'][match.required_level];
            html += `<li class="partial-match">${match.skill} (Has: ${candidateLevel}, Required: ${requiredLevel})</li>`;
        });
        html += `</ul></div>`;
    }

    if (result.missing_skills && result.missing_skills.length > 0) {
        html += `
            <div style="margin-bottom: 15px;">
                <strong style="color: #742a2a;">✗ Missing Skills:</strong>
                <ul class="skill-list">
        `;
        result.missing_skills.forEach(missing => {
            const requiredLevel = ['', 'Beginner', 'Intermediate', 'Advanced'][missing.required_level];
            html += `<li class="missing-skill">${missing.skill} (Required: ${requiredLevel})</li>`;
        });
        html += `</ul></div>`;
    }

    html += `
            </div>
        </div>
    `;

    return html;
}

function toggleExplanation(id) {
    const element = document.getElementById(id);
    if (element.style.display === 'none') {
        element.style.display = 'table-row';
    } else {
        element.style.display = 'none';
    }
}

// Initialize results on page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('resultsContainer')) {
        loadResults();
    }
});