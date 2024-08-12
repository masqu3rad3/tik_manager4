python.Execute "
import sys
tik_path = 'PATH//TO//PARENT//FOLDER//OF//TIKMANAGER4//'
if not tik_path in sys.path:
    sys.path.append(tik_path)
"