from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import uuid

app = Flask(__name__)


TASK_FILE = "task.xlsx"

# 初始化 task.xlsx
if not os.path.exists(TASK_FILE):
    df = pd.DataFrame(columns=["Date", "Task", "Location", "Priority", "Subtask 1", "Subtask 2", "Subtask 3", "ID"])
    df.to_excel(TASK_FILE, index=False)
else:
    df = pd.read_excel(TASK_FILE)
    if "ID" not in df.columns:
        df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
        df.to_excel(TASK_FILE, index=False)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/task", methods=["GET", "POST"])
def task():
    if request.method == "POST":
        date = request.form["date"]
        task = request.form["task"]
        location = request.form["location"]
        priority = request.form["priorty"]
        detail_1 = str(request.form["detail_1"])
        detail_2 = str(request.form["detail_2"])
        detail_3 = str(request.form["detail_3"])

        # 生成唯一 ID
        unique_id = str(uuid.uuid4())

        # 新增事件到 DataFrame
        new_event = pd.DataFrame([{
            "ID": unique_id,  # 新增 ID
            "Date": date,
            "Task": task,
            "Location": location,
            "Priority": int(priority),
            "Subtask 1": str(detail_1),
            "Subtask 2": str(detail_2),
            "Subtask 3": str(detail_3),
        }])

        


        # 使用 pd.concat 更新excel
        df = pd.read_excel(TASK_FILE)
        updated_df = pd.concat([df, new_event], ignore_index=True)
        updated_df.to_excel(TASK_FILE, index=False)

      

        # 跳轉到第三頁，傳遞所選日期
        return redirect(url_for("tasks_on_date", date=date))
    return render_template("task.html")





@app.route("/tasks_on_date")
def tasks_on_date():
    selected_date = request.args.get("date", "")  # 獲取 URL 中的日期參數
    
    tasks_for_date = []
    if selected_date:
        df = pd.read_excel(TASK_FILE)  # 讀取最新的任務文件
        
        # 確保日期欄位格式一致
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        tasks_for_date = df[df["Date"] == selected_date].copy()

        # 計算進度百分比
        def calculate_progress(row):
            subtasks = [row.get("Subtask 1"), row.get("Subtask 2"), row.get("Subtask 3")]
            total = sum(1 for task in subtasks if pd.notna(task))
            completed = sum(1 for task in subtasks if pd.notna(task) and task.endswith("(完成)"))
            return int((completed / total) * 100) if total > 0 else 0

        tasks_for_date["progress"] = tasks_for_date.apply(calculate_progress, axis=1)
        tasks_for_date = tasks_for_date[["ID", "Task", "Priority", "progress"]].to_dict(orient="records")
        tasks_for_date = sorted(tasks_for_date, key=lambda x: x["Priority"], reverse=True)
        
    return render_template("tasks_on_date.html", tasks=tasks_for_date, selected_date=selected_date)

    

@app.route("/complete_subtask/<subtask_id>", methods=["POST"])
def complete_subtask(subtask_id):
    df = pd.read_excel(TASK_FILE)
    for idx, row in df.iterrows():
        for subtask_col in ["Subtask 1", "Subtask 2", "Subtask 3"]:
            if row[subtask_col] == subtask_id:
                df.at[idx, subtask_col] += " (完成)"
                df.to_excel(TASK_FILE, index=False)
                return "OK", 200
    return "Subtask not found", 404


    


@app.route("/task_details")
def task_details():
    task_id = request.args.get('task_id', '')

    try:
        # 讀取任務文件
        df = pd.read_excel(TASK_FILE)
        task = df[df['ID'] == task_id]

        if task.empty:
            return f"Task '{task_id}' not found", 404

        task_name = task["Task"].iloc[0]
        subtasks = [
            {"id": task["Subtask 1"].iloc[0], "name": task["Subtask 1"].iloc[0], "completed": "(完成)" in task["Subtask 1"].iloc[0]},
            {"id": task["Subtask 2"].iloc[0], "name": task["Subtask 2"].iloc[0], "completed": "(完成)" in task["Subtask 2"].iloc[0]},
            {"id": task["Subtask 3"].iloc[0], "name": task["Subtask 3"].iloc[0], "completed": "(完成)" in task["Subtask 3"].iloc[0]},
        ]
        selected_date = task['Date'].iloc[0]
        location = task['Location'].iloc[0]

        # 新增天氣預報功能
        from weather import get_weather_forecast
        api_key = "CWA-78325D64-8216-4195-BA5A-03325ECBF818"  # 建議將 API Key 移至環境變數
        target_time = selected_date + " 06:00:00"
        
        try:
            weather_data = get_weather_forecast(location, target_time, api_key)
        except Exception as weather_error:
            weather_data = {"error": str(weather_error)}
        
    except Exception as e:
        return f"An error occurred: {e}", 500

    return render_template(
        'task_details.html',
        task_name=task_name,
        subtasks=subtasks,
        selected_date=selected_date,
        location=location,
        weather_data=weather_data
    )







if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
