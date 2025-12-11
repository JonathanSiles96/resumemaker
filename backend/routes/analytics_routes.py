"""
Analytics API Routes
Tracks page views, events, and provides admin dashboard stats
"""
from flask import Blueprint, request, jsonify
from models import db, User, Payment
from models.analytics import PageView, UsageEvent
import hashlib
import os

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Admin secret key for accessing stats (set in .env)
ADMIN_KEY = os.getenv('ANALYTICS_ADMIN_KEY', 'change-this-secret-key')


def hash_ip(ip):
    """Hash IP for privacy"""
    if not ip:
        return None
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


@analytics_bp.route('/track', methods=['POST'])
def track_pageview():
    """Track a page view (called from frontend)"""
    try:
        data = request.json or {}
        
        # Get visitor info
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            ip = ip.split(',')[0].strip()
        
        PageView.log_view(
            path=data.get('path', '/'),
            ip_hash=hash_ip(ip),
            user_agent=request.headers.get('User-Agent', '')[:500],
            referrer=data.get('referrer', request.headers.get('Referer', ''))[:500]
        )
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Analytics track error: {e}")
        return jsonify({'success': False}), 500


@analytics_bp.route('/event', methods=['POST'])
def track_event():
    """Track a usage event"""
    try:
        data = request.json or {}
        
        UsageEvent.log_event(
            event_type=data.get('event', 'unknown'),
            user_email=data.get('email'),
            event_metadata=data.get('metadata')
        )
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Analytics event error: {e}")
        return jsonify({'success': False}), 500


@analytics_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get analytics stats (requires admin key)"""
    # Check admin authorization
    auth_key = request.headers.get('X-Admin-Key') or request.args.get('key')
    if auth_key != ADMIN_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        days = int(request.args.get('days', 30))
        
        # Get page view stats
        page_stats = PageView.get_stats(days)
        
        # Get event stats
        event_stats = UsageEvent.get_event_stats(days)
        
        # Get user stats
        total_users = User.query.count()
        paid_users = User.query.filter_by(is_paid=True).count()
        free_users_converted = User.query.filter(User.free_generations_used > 0, User.is_paid == False).count()
        
        # Get payment stats
        total_revenue = db.session.query(
            db.func.sum(Payment.amount)
        ).filter_by(status='completed').scalar() or 0
        
        total_payments = Payment.query.filter_by(status='completed').count()
        
        return jsonify({
            'success': True,
            'period_days': days,
            'page_views': page_stats,
            'events': event_stats,
            'users': {
                'total': total_users,
                'paid': paid_users,
                'free_used_not_paid': free_users_converted,
                'conversion_rate': round((paid_users / total_users * 100), 2) if total_users > 0 else 0
            },
            'revenue': {
                'total': total_revenue,
                'payments_count': total_payments,
                'average_payment': round(total_revenue / total_payments, 2) if total_payments > 0 else 0
            }
        })
        
    except Exception as e:
        print(f"Analytics stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Simple HTML dashboard for analytics"""
    auth_key = request.args.get('key')
    if auth_key != ADMIN_KEY:
        return """
        <html>
        <head><title>Analytics - Login</title></head>
        <body style="font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f0f0;">
            <form style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>🔐 Analytics Dashboard</h2>
                <input type="password" name="key" placeholder="Enter admin key" style="padding: 10px; width: 250px; margin: 10px 0;">
                <button type="submit" style="padding: 10px 20px; background: #667eea; color: white; border: none; cursor: pointer; border-radius: 5px;">Login</button>
            </form>
        </body>
        </html>
        """, 200
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Maker - Analytics Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1 {{ color: #333; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .stat-card h3 {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
            .stat-card .value {{ font-size: 36px; font-weight: 700; color: #333; }}
            .stat-card.highlight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .stat-card.highlight h3, .stat-card.highlight .value {{ color: white; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            #viewsChart {{ width: 100%; height: 300px; }}
            .refresh-btn {{ padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 20px; }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>📊 Resume Maker Analytics</h1>
            <button class="refresh-btn" onclick="loadStats()">🔄 Refresh</button>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card"><h3>Loading...</h3><div class="value">-</div></div>
            </div>
            
            <div class="chart-container">
                <h3 style="margin-bottom: 15px;">Page Views (Last 30 Days)</h3>
                <canvas id="viewsChart"></canvas>
            </div>
        </div>
        
        <script>
            const API_KEY = '{auth_key}';
            let chart = null;
            
            async function loadStats() {{
                try {{
                    const response = await fetch('/api/analytics/stats?key=' + API_KEY);
                    const data = await response.json();
                    
                    if (data.success) {{
                        renderStats(data);
                        renderChart(data.page_views.views_by_day);
                    }}
                }} catch (e) {{
                    console.error('Error loading stats:', e);
                }}
            }}
            
            function renderStats(data) {{
                const grid = document.getElementById('statsGrid');
                grid.innerHTML = `
                    <div class="stat-card highlight">
                        <h3>💰 Total Revenue</h3>
                        <div class="value">$${{data.revenue.total.toFixed(2)}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>👥 Total Users</h3>
                        <div class="value">${{data.users.total}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>💎 Paid Users</h3>
                        <div class="value">${{data.users.paid}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>📈 Conversion Rate</h3>
                        <div class="value">${{data.users.conversion_rate}}%</div>
                    </div>
                    <div class="stat-card">
                        <h3>👁️ Page Views (30d)</h3>
                        <div class="value">${{data.page_views.total_views}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>🧑 Unique Visitors (30d)</h3>
                        <div class="value">${{data.page_views.unique_visitors}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>📄 Resumes Generated</h3>
                        <div class="value">${{data.events.event_counts.resume_generated || 0}}</div>
                    </div>
                    <div class="stat-card">
                        <h3>💳 Payments</h3>
                        <div class="value">${{data.revenue.payments_count}}</div>
                    </div>
                `;
            }}
            
            function renderChart(viewsData) {{
                const ctx = document.getElementById('viewsChart').getContext('2d');
                
                if (chart) chart.destroy();
                
                chart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: viewsData.map(v => v.date),
                        datasets: [{{
                            label: 'Page Views',
                            data: viewsData.map(v => v.views),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});
            }}
            
            loadStats();
        </script>
    </body>
    </html>
    """, 200

