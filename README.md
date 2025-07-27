# CL-AI-MVP
### 1  Create a new GPU Docker Space
- Space type: **Docker**
- Hardware: **GPU (T4‑small is fine)**

### 2  Add repo files & push
```bash
git lfs install
git clone https://huggingface.co/spaces/<YOUR-ORG>/avatar-slides
cd avatar-slides
# paste files above
git add .
git commit -m "initial MVP"
git push
```
