@echo off
echo 🚀 Starting TrustChain Distributed Network...
start cmd /k "title NODE 5001 && python api.py 5001"
start cmd /k "title NODE 5002 && python api.py 5002"
start cmd /k "title NODE 5003 && python api.py 5003"
start cmd /k "title STREAMLIT DASHBOARD && streamlit run app.py"
echo 🌐 Network launched! (Ports 5001, 5002, 5003 + UI)
pause
