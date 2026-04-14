import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown
import uvicorn

app = FastAPI(title="MarkItDown Web Service")

# 初始化 MarkItDown 实例
# 为了节省内存，我们只初始化一次
md = MarkItDown()

# 静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MarkItDown Web Service</h1><p>请检查 static/index.html 是否存在。</p>"

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    """
    接收上传的文件并转换为 Markdown。
    优化点：
    1. 使用临时文件并在转换后立即删除。
    2. 限制文件处理流，避免大文件撑爆内存。
    """
    # 获取文件后缀名
    suffix = os.path.splitext(file.filename)[1]
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        try:
            # 流式写入临时文件，节省内存
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
            # 确保文件已写入并关闭，以便 markitdown 读取
            tmp.close()
            
            # 执行转换
            result = md.convert(tmp_path)
            
            return {
                "filename": file.filename,
                "content": result.text_content,
                "status": "success"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # 无论成功还是失败，都清理临时文件
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # 配置优化：单工作进程运行，限制并发连接，适合低内存 NAS
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
