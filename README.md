# Calendar

 ```
Calendar/
│
├── app.py           # 主 Flask 應用程式文件
├── task.xlsx           
├── templates/
│   ├── task.html    #新增或編輯事件，提供表單介面輸入
│   ├── task_details.html    #當使用者在task_on_date.html點選指定任務，會顯示該任務的所有子任務
│   ├── task_on_date.html    #當使用者在index.html點選指定日期，會顯示當天的所有任務
│   └── index.html   #主頁面，顯示日曆       
└── static/
    ├── styles.css         # CSS 文件
    ├── sea.jpg         # 背景圖
    └── calendar.js        
```
