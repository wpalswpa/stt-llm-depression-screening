# 상담 음성 전사와 LLM 분류의 품질 검증

한국어 복지상담 음성을 Whisper로 전사하고 GPT 계열 모델의 zero-shot 분류를 비교한 석사 연구입니다. 2025 한국통신학회 하계종합학술발표회 발표 이후 전사 처리와 평가 코드를 다시 점검했습니다. 의료 진단이나 임상 성능을 검증한 서비스는 아닙니다.

## 문제와 접근

음성 기반 분류에서는 전사 오류와 분류 오류가 섞입니다. 따라서 Whisper 전사의 WER·CER와 LLM의 정확도·우울 라벨 F1을 따로 확인합니다.

```text
상담 WAV + 정답 JSON → Whisper tiny → 전사 품질 측정
                                       ↓
                              전사 텍스트 → GPT zero-shot → 분류 평가
```

연구에서 Whisper·Scikit-LLM 실험, 분류 모델 비교 및 결과 정리를 수행했습니다. 음성 원본·상담 내용·개인별 결과는 공개하지 않습니다.

## 먼저 확인할 파일

| 파일 | 내용 |
|---|---|
| [연구 노트북](notebooks/LLM_우울증_조기진단_최종정리본.ipynb) | 전사, 텍스트 구성, GPT 비교, 그래프 |
| [evaluation.py](evaluation.py) | 이미 생성한 CSV의 전사 오류율을 오프라인 재평가 |
| [tests/test_evaluation.py](tests/test_evaluation.py) | 빈 전사·정답 누락·잘못된 입력의 회귀 검사 |
| [과거 결과 표](assets/results.png) | 기존 보고 수치. 수정한 코드의 재실행 결과가 아님 |

## 실행

Python 3.12. 아래 검사는 표준 라이브러리만 사용하며 API 키와 원본 음성이 필요 없습니다.

```bash
git clone https://github.com/wpalswpa/stt-llm-depression-screening.git
cd stt-llm-depression-screening
python -m unittest discover -s tests -v
python evaluation.py /path/to/depression_stt_result.csv
```

CSV 필수 열은 `gt_text,pred_text`입니다. 두 열의 공백을 정규화한 뒤 행별 WER·CER의 산술평균을 계산합니다(CER에는 단어 사이 공백 포함). 빈 전사는 삭제 오류로 계산하고, 빈 정답은 제외 건수를 별도 출력합니다. 전체 정답이 없으면 실패합니다. 이 명령은 전사나 분류를 새로 수행하지 않습니다.

전체 연구 노트북은 Colab 경로와 Drive 마운트를 사용합니다. `evaluation.py`를 Colab의 `/content`에 함께 업로드하거나 저장소를 복제해 import 경로를 맞춥니다. AI Hub에서 허가받은 데이터를 준비하고 ZIP 경로·폴더 구조·정답 JSON 형식을 먼저 맞춰야 합니다. API 키는 실행 환경의 `OPENAI_API_KEY`에 설정합니다. Colab Secrets를 사용하면 환경변수에 명시적으로 연결해야 합니다. 분류 셀은 외부 API 호출 비용이 발생합니다.

## 기존 수치와 이번 수정의 구분

기존 보고: Whisper-tiny WER **0.5847**, CER **0.2542**; GPT-3.5-turbo 정확도 **0.5705**, 우울 라벨 F1 **0.3687**; GPT-4o 정확도 **0.5747**, F1 **0.3120**. 원본 데이터와 실행 로그가 공개 저장소에 없어 이 수치를 독립적으로 재현할 수 없습니다.

2026-09-16 코드 점검에서 다음을 수정했습니다.

- 빈 전사를 WER·CER에서 제외하던 조건을 수정했습니다. 이를 제외하면 실패가 평균에서 사라집니다.
- 정답 JSON의 첫 `inputText`만 읽던 부분을 전체 세그먼트로 확장하고, 압축 해제·전사 입력 경로를 일치시켰습니다.
- 실행 모델 GPT-4o와 결과 표의 GPT-4o-mini 명칭 불일치, 혼동행렬의 실제/예측 축 표기를 바로잡았습니다.
- 고정 조직 ID를 선택적 환경변수로 바꾸고 빠진 import를 추가했습니다.
- 8개 합성 입력 회귀 검사와 GitHub Actions를 추가했습니다.

**수정 후 음성 재전사와 LLM 재평가는 아직 수행하지 않았습니다.** 기존 수치는 역사적 보고치이며 수정된 파이프라인의 성능으로 인용하지 않습니다. 전사 오류가 분류 저하의 원인이라는 설명 역시 정답 전사/모델 전사를 동일 조건으로 비교하기 전에는 가설입니다.

추가 확인: 파일 이름을 `speaker_id`로 사용한 기존 집계가 실제 화자 단위와 일치하는지, JSON 세그먼트 순서가 시간순인지 원본 메타데이터로 확인해야 합니다. 상위 Whisper 모델과의 비교 및 LLM 모델·프롬프트·라이브러리 버전 고정은 후속 실험 범위입니다.
