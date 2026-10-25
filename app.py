import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="삼진제약 사업구조·수금관리 분석기", page_icon="💊", layout="wide")
st.title("💊 삼진제약 사업구조 및 수금관리 분석기")
st.caption("공시자료 기반 분석 · 2023~2025년 연간 및 2026년 상반기 · 단위: 억 원")
st.info("실제 공시 수치와 사용자 가정에 따른 시뮬레이션을 구분합니다. 내부 수금원장 없이 거래처별 실제 회수일이나 미래 현금흐름을 확정할 수 없습니다.")

# 매출 및 수주상황 표: 원자료 백만원 → 억원(÷100)
# 출처: 2025 사업보고서(2026.03.16), 2026 반기보고서(2026.08.14)
# 2023~2025: 연간 / 2026H1: 상반기
raw_sales = {
    "2023": {"정제":161663,"주사제":40935,"캡슐제":42831,"기타제형":5075,"상품":24769,"기타":16856,"합계":292129},
    "2024": {"정제":163664,"주사제":48512,"캡슐제":40082,"기타제형":5300,"상품":30476,"기타":20316,"합계":308350},
    "2025": {"정제":167849,"주사제":46565,"캡슐제":38185,"기타제형":4378,"상품":36603,"기타":15554,"합계":309134},
    "2026 상반기": {"정제":84069,"주사제":19979,"캡슐제":18230,"기타제형":2071,"상품":16053,"기타":7302,"합계":147704},
}
sales = pd.DataFrame(raw_sales).T / 100
sales["제품"] = sales[["정제","주사제","캡슐제","기타제형"]].sum(axis=1)
sales["상품 비중(%)"] = sales["상품"] / sales["합계"] * 100
sales["제품 비중(%)"] = sales["제품"] / sales["합계"] * 100

# 재무제표 주석 6 '매출채권및기타채권' 중 유동 매출채권의 순장부금액.
# 천원 → 억원(÷100,000). 2023, 2024, 2025 연말 / 2026 6월 말
# 2023 값은 주석을 검증하기 전까지 미입력. 따라서 2024 DSO도 산출하지 않음.
ar_net = {"2024":624.98293, "2025":602.61968, "2026 상반기":557.32375}

tab1, tab2, tab3, tab4 = st.tabs(["① 매출구조", "② 매출채권", "③ 수금 시뮬레이션", "④ 종합 분석"])

with tab1:
    st.subheader("제품·상품 매출구조 변화")
    st.caption("제품은 직접 제조한 품목, 상품은 매입해 판매하는 품목입니다. '기타' 매출은 별도로 유지합니다.")
    annual = sales.loc[["2023","2024","2025"]]
    c1,c2,c3=st.columns(3)
    c1.metric("2025년 매출액",f"{sales.loc['2025','합계']:,.1f}억 원")
    c2.metric("2025년 상품 매출 비중",f"{sales.loc['2025','상품 비중(%)']:.2f}%",f"{sales.loc['2025','상품 비중(%)']-sales.loc['2024','상품 비중(%)']:+.2f}%p")
    c3.metric("2023→2025 상품 매출 증가율",f"{(sales.loc['2025','상품']/sales.loc['2023','상품']-1)*100:+.1f}%")
    fig=px.bar(annual.reset_index().rename(columns={"index":"연도"}),x="연도",y=["제품","상품","기타"],barmode="stack",labels={"value":"매출액(억 원)","variable":"구분"})
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(sales[["제품","상품","기타","합계","상품 비중(%)"]].style.format("{:,.2f}"),use_container_width=True)
    st.warning("2026년 상반기는 6개월 실적이므로 연간 매출액과 직접 증감률 비교하지 않습니다. 상품 매출은 의료기기·건강기능식품 매출과 동의어가 아닙니다.")
    st.caption("출처: 2025년 사업보고서 및 2026년 반기보고서, II. 사업의 내용 → 4. 매출 및 수주상황")

with tab2:
    st.subheader("매출채권 회수 효율성")
    st.caption("기타채권을 제외한 순매출채권을 사용합니다. 2026년 상반기는 181일 기준이며 연환산 매출을 임의 적용하지 않습니다.")
    ar_df=pd.DataFrame({"기말 순매출채권(억 원)":ar_net})
    st.dataframe(ar_df.style.format("{:,.2f}"),use_container_width=True)
    st.line_chart(ar_df)
    dso25=((ar_net["2024"]+ar_net["2025"])/2)/sales.loc["2025","합계"]*365
    dso26=((ar_net["2025"]+ar_net["2026 상반기"])/2)/sales.loc["2026 상반기","합계"]*181
    a,b=st.columns(2)
    a.metric("2025년 추정 DSO",f"{dso25:.1f}일")
    b.metric("2026년 상반기 추정 DSO",f"{dso26:.1f}일")
    st.caption("DSO = (기초·기말 순매출채권 평균 ÷ 해당 기간 매출액) × 기간 일수. 매출액은 외상매출만 분리되지 않아 전체 매출액을 대용합니다.")
    st.caption("두 기간의 DSO는 기간 구성·매출 계절성 차이가 있으므로 개선 여부를 단정하지 않습니다. 2023년 말 잔액 미검증으로 2024년 DSO는 제외했습니다.")
    st.caption("출처: 2025년 사업보고서 및 2026년 반기보고서, III. 재무에 관한 사항 → 주석 6")

with tab3:
    st.subheader("회수기간 변화에 따른 운전자금 점유액")
    st.info("아래는 사용자 가정에 따른 계산입니다. 실제 수금액, 신규 현금 창출액 또는 확정된 현금 유입 예측이 아닙니다.")
    baseline=st.selectbox("기준 실적",["2025","2026 상반기"],index=0)
    days=365 if baseline=="2025" else 181
    base_sales=float(sales.loc[baseline,"합계"])
    base_dso=dso25 if baseline=="2025" else dso26
    c1,c2=st.columns(2)
    with c1:
        growth=st.slider("매출 변화율 가정 (%)",-30,50,0,1)
        reduction=st.slider("회수기간 단축 가정 (일)",0,30,5,1)
    with c2:
        assumed_dso=st.number_input("기준 회수기간 (일, 수정 가능)",min_value=1.0,max_value=365.0,value=round(base_dso,1),step=0.5)
        st.caption("기본값은 공시자료로 계산한 추정 DSO입니다.")
    scenario_sales=base_sales*(1+growth/100)
    new_dso=max(0,assumed_dso-reduction)
    before=scenario_sales/days*assumed_dso
    after=scenario_sales/days*new_dso
    released=before-after
    x,y,z=st.columns(3)
    x.metric("가정 매출액",f"{scenario_sales:,.1f}억 원")
    y.metric("변경 후 회수기간",f"{new_dso:.1f}일")
    z.metric("운전자금 점유액 감소 추정",f"{released:,.1f}억 원")
    st.bar_chart(pd.DataFrame({"추정 점유액(억 원)":[before,after]},index=["변경 전","변경 후"]))
    st.write(f"매출액 {scenario_sales:,.1f}억 원, 회수기간 {assumed_dso:.1f}→{new_dso:.1f}일을 가정하면, 매출채권에 묶이는 평균 운전자금은 약 **{released:,.1f}억 원 감소**하는 것으로 추정됩니다.")
    st.caption("산식: 매출액 ÷ 기간 일수 × 회수기간. 매출이 균등하게 발생하고 매출 구성·회수 조건이 일정하다고 가정한 단순 모형입니다.")

with tab4:
    st.subheader("자금관리 관점의 종합 해석")
    st.write(f"**확인된 사실 1.** 상품 매출액은 2023년 {sales.loc['2023','상품']:,.1f}억 원에서 2025년 {sales.loc['2025','상품']:,.1f}억 원으로 증가했습니다.")
    st.write(f"**확인된 사실 2.** 순매출채권은 2025년 말 {ar_net['2025']:,.1f}억 원에서 2026년 6월 말 {ar_net['2026 상반기']:,.1f}억 원으로 감소했습니다.")
    st.write("**추가 확인 과제.** 제품·상품별 수금 조건, 도매·병원별 채권 연령, 실제 수금 예정일, 연체 및 반품·할인 조건은 공시만으로 확인할 수 없습니다.")
    st.write("**실무 연결.** 사업구조 변화와 함께 거래처별 수금 계획을 점검하고, 회수 지연 가능성을 조기에 식별하는 것이 자금관리 직무의 핵심입니다.")
    st.success("자기소개서 활용 메시지: 생성형 AI를 활용해 삼진제약의 매출구조와 매출채권을 분석하고, 회수기간 변화에 따른 운전자금 부담을 시뮬레이션하는 프로그램을 구현했습니다.")
    st.caption("분석상 인과관계를 주장하지 않습니다. 상품 매출 증가가 매출채권 감소를 일으켰다고 볼 수는 없습니다.")

with st.expander("데이터 출처 및 해석상 한계"):
    st.markdown("""
    - 삼진제약 사업보고서(2026.03.16): 2023~2025 매출 및 수주상황, 2024~2025 매출채권 주석.
    - 삼진제약 반기보고서(2026.08.14): 2026년 상반기 매출 및 수주상황, 2026년 6월 말 매출채권 주석.
    - 금액 환산: 매출 원자료 백만원 → 억원(100으로 나눔), 매출채권 원자료 천원 → 억원(100,000으로 나눔).
    - 제품·상품별 개별 채권 잔액이나 수금조건은 공시되지 않아 제품·상품별 DSO는 계산하지 않습니다.
    - 계산값은 자금관리 교육·자기소개서 목적의 추정치이며 회사의 내부 관리지표가 아닙니다.
    """)
