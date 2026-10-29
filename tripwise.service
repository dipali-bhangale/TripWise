[Unit]
Description=TripWise Streamlit
After=network.target
[Service]
User=www-data
WorkingDirectory=/opt/tripwise
ExecStart=/opt/tripwise/.venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501
Restart=always
[Install]
WantedBy=multi-user.target
