/**
 * PM2 Ecosystem Configuration for Resume Maker
 * 
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 restart resumemaker
 *   pm2 logs resumemaker
 *   pm2 stop resumemaker
 */

module.exports = {
  apps: [{
    name: 'resumemaker',
    cwd: './backend',
    script: 'venv/bin/gunicorn',
    args: '-w 4 -b 127.0.0.1:5000 --timeout 300 --access-logfile - --error-logfile - app:app',
    interpreter: 'none',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      FLASK_ENV: 'production',
      FLASK_DEBUG: 'False'
    },
    error_file: './logs/error.log',
    out_file: './logs/access.log',
    time: true,
    // Graceful shutdown
    kill_timeout: 5000,
    wait_ready: true,
    listen_timeout: 10000
  }]
};

