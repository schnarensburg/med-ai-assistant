# Interview Conduction

## 1. Set User-ID
In `app.py` **line 413**:
```python
USER_ID = "<NEW_USER_ID>"
```
If an error occurs, a wrong `User_ID` might be the cause.

---

## 2. Start the backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 3. Start the frontend
```bash
streamlit run app.py --server.port 8501
```

---

## 4. Start ngrok (for external access)
```bash
ngrok http 8501
```
The output will contain a public **https://...ngrok-free.app** URL.  
Open this URL in the browser on the other PC.

---

## 5. If “port already in use” error occurs
```bash
sudo pkill -f "uvicorn|streamlit"
sudo fuser -k 8000/tcp 8501/tcp
pkill ngrok
```

---

## 6. Load a new interview round
1. Copy all code from `round_x.py` (`Ctrl+A`, `Ctrl+C`).
2. Paste it into `router_engine_simple.py` (`Ctrl+A`, `Ctrl+V` → replace all content).
3. Save the file.
4. Reload the Streamlit page in the browser.

---

**Port overview**
- **8000** – Backend (FastAPI)
- **8501** – Frontend (Streamlit)
- **ngrok** should always be started for the port you want to make externally accessible (usually 8501).
