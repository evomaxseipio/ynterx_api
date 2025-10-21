module.exports = {
  apps: [{
    name: 'ynterx-api',
    script: 'app/main.py',
    interpreter: 'python3',
    cwd: '/root/project/ynterx-api',
    instances: 1,
    autorestart: true,
    watch: false, // Deshabilitar file watching para evitar restarts
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      PORT: 8000,
      USE_GOOGLE_DRIVE: 'true' // Forzar uso de Google Drive
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 8001,
      USE_GOOGLE_DRIVE: 'true' // Forzar uso de Google Drive
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    // Configuración para evitar problemas con archivos generados
    ignore_watch: [
      'app/generated_contracts',
      'logs',
      'node_modules',
      'venv',
      '.git',
      '**/*.docx',
      '**/*.pdf'
    ]
  }]
};
