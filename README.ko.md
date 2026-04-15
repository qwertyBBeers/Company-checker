# Company Tracker

[한국어](README.ko.md) | [English](README.en.md)

PyQt6로 만든 Windows용 취업 준비 일정 관리 위젯입니다.

작게 떠 있는 위젯 형태로 면접 D-Day를 확인하다가, 필요할 때 창을 확장해서 회사별 메모, 면접 정보, 링크를 함께 관리할 수 있습니다.

## 미리보기

### 축소 모드

![축소 모드](image.png)

### 확장 모드

![확장 모드](image2.png)

## 주요 기능

- 축소 모드에서 회사별 D-Day 카운트다운 확인
- 확장 모드에서 회사별 상세 메모 작성
- 실시간 초 단위 D-Day 갱신
- 회사 추가 / 삭제
- 드래그 앤 드롭 순서 변경
- 면접 일정 임박순 자동 정렬
- 프레임 없는 위젯 스타일 창
- 항상 위 옵션
- 라이트 / 다크 모드 전환
- 로컬 JSON 저장
- Windows `.exe` 패키징 스크립트 포함

## 기술 스택

- Python 3.x
- PyQt6
- JSON 파일 저장
- PyInstaller

## 프로젝트 구조

```text
app.py
requirements.txt
build_windows.bat
build_windows.ps1
README.md
README.ko.md
README.en.md
README_WINDOWS_BUILD.md
scripts/
  generate_icon.py
dday_data.example.json
image.png
image2.png
```

## 실행 방법

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Windows용 exe 빌드

Windows에서 아래 둘 중 하나를 실행하면 됩니다.

```powershell
build_windows.bat
```

또는

```powershell
.\build_windows.ps1
```

빌드가 끝나면 실행 파일은 아래 경로에 생성됩니다.

```text
dist\CompanyTracker\CompanyTracker.exe
```

추가 패키징 메모는 [README_WINDOWS_BUILD.md](README_WINDOWS_BUILD.md)에 정리되어 있습니다.

## 데이터 파일

실행 데이터는 `dday_data.json`에 저장됩니다.

- `dday_data.json`은 git에 포함되지 않습니다.
- `dday_data.example.json`은 예시 파일입니다.

## git 업로드 참고

현재 `.gitignore`에 아래 항목들이 제외되도록 설정되어 있습니다.

- `.venv/`
- `__pycache__/`
- `dist/`
- `build/`
- `assets/`
- `dday_data.json`
