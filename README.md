Interview Conduction
1. for new interviewpartner: change User_ID in line 413 in app.py (if an error occurs this can be the reason as not sufficientl tested yet)
1. Follow Instuction for ngronk 
2. Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
streamlit run app.py --server.port 8502
3. Start frondend
streamlit run app.py --server.port 8502

4. Start gronk
ngrok http 8501

if error already in use occurs: 

sudo pkill -f "uvicorn\|streamlit"
sudo fuser -k 8000/tcp 8001/tcp 8502/tcp
pkill ngrok
4. For each round: Insert code of current round (round_x.py) via copy paste (strg A, strg c, strg v in router_engine_simple) in router_engine_simple fully
5. Save changes for each ropund
6. The user has to reload streamlit page for each round to receive updated code

