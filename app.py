import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='삼진제약 코프로모션 자금수지 시뮬레이터', page_icon='💊', layout='wide')
st.title('💊 삼진제약 코프로모션 확대에 따른 자금수지 시뮬레이터')
st.caption('공시 실적과 가정 기반 사업 시나리오를 구분한 자금관리·수납관리 분석 도구 | 금액 단위: 억 원')

# 출처: 삼진제약 2025 사업보고서(2026.03.16) '매출 및 수주상황' 표
# 원 공시 단위 백만원 -> 억원: 100으로 나눔. '상품'은 코프로모션 매출과 동의어가 아님.
SALES = {
    '2023': {'제품': 2505.04, '상품': 247.69, '기타': 168.56, '합계': 2921.29},
    '2024': {'제품': 2575.58, '상품': 304.76, '기타': 203.16, '합계': 3083.50},
    '2025': {'제품': 2569.77, '상품': 366.03, '기타': 155.54, '합계': 3091.34},
}
# 제품 합계는 제형별 합산; 2025: 167849+46565+38185+4378=256977 (백만원)
# 2024: 163664+48512+40082+5300=257558
# 2023: 161663+40935+42831+5075=250504
sales = pd.DataFrame(SALES).T
sales['상품 비중(%)'] = sales['상품'] / sales['합계'] * 100

st.info('**구분 원칙:** 과거 매출·상품 비중은 공시 사실입니다. 코프로모션의 매출 규모·매입원가율·지급/회수조건은 **사용자가 입력한 가상 조건**이며 실제 계약조건이나 회사의 공식 자금계획이 아닙니다. 공시의 ‘상품 매출’ 전체를 코프로모션 매출로 간주하지 않습니다.')

t0, t1, t2, t3, t4 = st.tabs(['📘 개요', '① 삼진제약 사업구조', '② 코프로모션 시나리오', '③ 월별 자금수지', '④ 자금관리 활용'])

with t0:
    st.header('프로그램 개발 배경')
    st.write('삼진제약의 코프로모션 확대 방향에 주목했습니다. 외부 제품의 판매 확대는 매출뿐 아니라 매입대금 지급 시점, 판매대금 회수 시점에 따라 자금 부담이 달라질 수 있습니다. 따라서 공시 매출구조를 확인하고, 가상의 코프로모션 사업을 추가했을 때 **언제 얼마의 현금이 들어오고 나가는지** 분석하도록 설계했습니다.')
    st.subheader('핵심 질문')
    st.markdown('**“코프로모션 매출이 성장해도 매입대금이 먼저 지급된다면, 월별 자금수지에는 어떤 공백이 생길까?”**')
    st.markdown('''**분석 흐름**
    1. 삼진제약의 공시 제품·상품 매출구조 확인
    2. 신규/확대 코프로모션 사업의 매출, 매입원가율, 지급·회수조건 입력
    3. 일별 현금 발생·결제 일정을 월별로 집계하고 누적 순현금흐름 분석
    4. 거래조건 개선에 따른 필요 운전자금과 유동성 대응 시사점 확인''')
    st.warning('분석은 신규 사업의 **증분 현금흐름**만 다룹니다. 회사 전체 현금잔액, 실제 코프로모션 계약금액, 기존 사업의 자금일보를 재현하지 않습니다.')

with t1:
    st.header('① 삼진제약 공시 매출구조')
    st.markdown('**왜 분석하나요?** 회사의 기존 제품·상품 매출 비중을 확인해 코프로모션 확대라는 사업 방향을 검토할 출발점을 마련합니다.')
    st.markdown('**어떻게 분석하나요?** 사업보고서의 제품(정제·주사제·캡슐제·기타제형), 상품, 기타 매출을 연도별로 비교합니다.')
    st.markdown('**얻을 수 있는 결론은?** 상품 매출이 확대된 사실은 확인할 수 있지만, 이 금액 전체가 코프로모션에서 발생했다고 결론내릴 수는 없습니다.')
    a,b,c=st.columns(3)
    a.metric('2025년 총매출',f"{sales.loc['2025','합계']:,.1f}억 원")
    b.metric('2025년 상품매출',f"{sales.loc['2025','상품']:,.1f}억 원")
    c.metric('2023→2025 상품매출 증가율',f"{(sales.loc['2025','상품']/sales.loc['2023','상품']-1)*100:.1f}%")
    chart=sales[['제품','상품','기타']].reset_index().rename(columns={'index':'연도'}).melt(id_vars='연도',var_name='매출구분',value_name='매출액')
    st.plotly_chart(px.bar(chart,x='연도',y='매출액',color='매출구분',barmode='stack',title='삼진제약 연간 매출구조 (억 원)'),use_container_width=True)
    st.dataframe(sales.style.format('{:,.2f}'),use_container_width=True)
    st.caption('출처: 삼진제약 2025 사업보고서, II. 사업의 내용 > 4. 매출 및 수주상황. 2023~2025 연간 실적. 공시 단위 백만원을 억원으로 환산.')

with t2:
    st.header('② 코프로모션 사업 확대 시나리오')
    st.markdown('**왜 분석하나요?** 매출 확대의 효과를 이익뿐 아니라 현금 유입·유출 시점으로 확인하기 위해서입니다.')
    st.markdown('**어떻게 분석하나요?** 연간 매출액을 월별로 균등 배분하고, 매입원가와 현금 회수·지급 시점을 일 단위로 계산합니다.')
    st.markdown('**얻을 수 있는 결론은?** 사업 규모가 같더라도 거래조건에 따라 현금 부족 구간과 운전자금 부담이 달라집니다.')
    st.caption('아래 값은 **전부 가상 시나리오 입력값**입니다. 실제 삼진제약의 코프로모션 계약조건이 아닙니다.')
    c1,c2=st.columns(2)
    with c1:
        annual_sales=st.number_input('신규/확대 사업 연간 매출 가정 (억 원)',min_value=0.0,max_value=3000.0,value=120.0,step=10.0)
        cost_ratio=st.slider('매입원가율 가정 (%)',30.0,95.0,87.0,1.0)
    with c2:
        payment_days=st.slider('매입대금 지급까지 소요일 (일)',0,150,80,5)
        collection_days=st.slider('판매대금 회수까지 소요일 (일)',0,180,105,5)
    st.caption('가정: 매출과 매입은 매월 동일한 금액으로 발생하고, 월중 매일 균등하게 배분됩니다. 매입대금은 매출에 비례하여 지급합니다. 판촉·운영비, 부가가치세·법인세·재고 선매입·반품·수수료·기존 잔액은 제외합니다.')

# 달력상 실제 월 일수로 2027년 1~12월 영업을 가정, 2028년까지 후속 수금/지급 추적
# 코프로모션 신규 사업의 증분 흐름만 계산. 2027은 가상의 시뮬레이션 연도이며 사업 계획 연도가 아님.
months=pd.period_range('2027-01',periods=12,freq='M')
monthly_sales=[annual_sales/12]*12
records=[]
for period,amt in zip(months,monthly_sales):
    dates=pd.date_range(period.start_time,period.end_time,freq='D')
    for d in dates:
        portion=amt/len(dates)
        records.append({'date':d+pd.Timedelta(days=collection_days),'type':'판매대금 수금','amount':portion})
        records.append({'date':d+pd.Timedelta(days=payment_days),'type':'매입대금 지급','amount':-portion*cost_ratio/100})

def summarize(records):
    frame=pd.DataFrame(records)
    frame['월']=frame['date'].dt.to_period('M').astype(str)
    pivot=frame.pivot_table(index='월',columns='type',values='amount',aggfunc='sum',fill_value=0)
    for name in ['판매대금 수금','매입대금 지급']:
        if name not in pivot:pivot[name]=0.0
    pivot=pivot.reindex(pd.period_range('2027-01','2028-04',freq='M').astype(str),fill_value=0.0)
    pivot['현금 유입']=pivot['판매대금 수금']
    pivot['현금 유출']=-pivot['매입대금 지급']
    pivot['월별 순현금흐름']=pivot['현금 유입']-pivot['현금 유출']
    pivot['누적 순현금흐름']=pivot['월별 순현금흐름'].cumsum()
    return pivot

cash=summarize(records)
max_gap=max(0.0,-cash['누적 순현금흐름'].min())
peak_month=cash['누적 순현금흐름'].idxmin()
end_2027=cash.loc['2027-12','누적 순현금흐름']

with t3:
    st.header('③ 월별 자금수지 및 필요 운전자금')
    st.markdown('**왜 분석하나요?** 사업 확대 과정에서 매출과 매입대금의 결제 시점이 달라 발생하는 현금 부족 구간을 찾기 위해서입니다.')
    st.markdown('**어떻게 분석하나요?** 각 월의 매출을 날짜별로 배분하고 입력한 회수·지급일만큼 이동시켜 현금흐름을 집계합니다.')
    st.markdown('**얻을 수 있는 결론은?** 시나리오에서 가장 큰 누적 현금 부족액과 그 발생 시점을 확인할 수 있습니다.')
    a,b,c=st.columns(3)
    a.metric('시나리오 최대 누적 자금 부족액',f'{max_gap:,.2f}억 원')
    b.metric('자금 부족 최대 시점',peak_month)
    c.metric('2027년 말 누적 순현금흐름',f'{end_2027:,.2f}억 원')
    st.plotly_chart(px.line(cash.reset_index().rename(columns={'index':'월'}),x='월',y='누적 순현금흐름',markers=True,title='월말 누적 순현금흐름 (억 원)'),use_container_width=True)
    plot=cash[['현금 유입','현금 유출']].reset_index().rename(columns={'index':'월'}).melt(id_vars='월',var_name='구분',value_name='금액')
    st.plotly_chart(px.bar(plot,x='월',y='금액',color='구분',barmode='group',title='월별 현금 유입·유출 (억 원)'),use_container_width=True)
    st.dataframe(cash[['현금 유입','현금 유출','월별 순현금흐름','누적 순현금흐름']].style.format('{:,.2f}'),use_container_width=True)
    st.caption('2027년은 계산 편의를 위한 가상 사업연도입니다. 2028년 후속 기간은 2027년 발생 매출·매입의 지연 결제를 반영하며, 신규 매출은 추가하지 않습니다. 최대 자금 부족액은 사업 자체의 현금흐름만 고려한 추정치로 실제 차입 필요액과 다릅니다.')

with t4:
    st.header('④ 거래조건 개선과 자금관리 활용')
    st.markdown('**왜 분석하나요?** 단순히 부족액을 확인하는 데서 그치지 않고 수금관리·자금수지 관리에 적용할 수 있는 개선 방향을 비교하기 위해서입니다.')
    improve=st.slider('판매대금 회수기간 단축 가정 (일)',0,min(60,collection_days),min(15,collection_days),5)
    revised=[]
    for rec in records:
        d=rec.copy()
        if d['type']=='판매대금 수금':d['date']=d['date']-pd.Timedelta(days=improve)
        revised.append(d)
    improved=summarize(revised)
    new_gap=max(0.0,-improved['누적 순현금흐름'].min())
    a,b,c=st.columns(3)
    a.metric('기존 최대 부족액',f'{max_gap:,.2f}억 원')
    b.metric('수금조건 개선 후 최대 부족액',f'{new_gap:,.2f}억 원')
    c.metric('최대 부족액 감소',f'{max_gap-new_gap:,.2f}억 원')
    compare=pd.DataFrame({'월':cash.index,'기존 조건':cash['누적 순현금흐름'].values,'수금기간 단축':improved['누적 순현금흐름'].values}).melt(id_vars='월',var_name='조건',value_name='누적 순현금흐름')
    st.plotly_chart(px.line(compare,x='월',y='누적 순현금흐름',color='조건',title='수금조건 개선 전·후 누적 현금흐름'),use_container_width=True)
    st.markdown('''**자금관리 직무에서 활용할 관점**
    - **수납관리:** 거래처별 회수 예정일과 실제 입금일의 차이를 점검해 수금 예측 정확도 개선
    - **자금관리·출납:** 매입대금 지급일과 수금일을 대조하여 자금 부족이 집중되는 시점 사전 확인
    - **차입금 현황 관리:** 예상 자금 부족 기간과 차입금 만기 일정을 함께 검토해 자금 운용 계획 지원
    - **유관부서 협업:** 영업·구매부서와 결제조건 및 회수 지연 사유 확인''')
    st.warning('회수기간 단축에 따른 **최대 부족액 감소**는 가정에 따른 시뮬레이션 결과입니다. 실제 수금 실적, 순이익 증가 또는 회사의 실제 자금 확보액을 의미하지 않습니다.')
    st.subheader('자기소개서에 연결할 핵심 메시지')
    st.write('“삼진제약의 코프로모션 확대 과정에서 매출 증가와 자금 유입 시점이 달라질 수 있다는 점에 주목했습니다. 생성형 AI를 활용해 매입대금 지급조건과 판매대금 회수조건에 따른 월별 자금수지를 분석하는 프로그램을 구현했습니다. 입사 후에도 수금일정과 일별 자금현황을 면밀히 점검하여 사업 확대를 안정적인 자금 운영으로 뒷받침하겠습니다.”')

with st.expander('공시 출처·산식·한계'):
    st.markdown('''- **공시 데이터:** 삼진제약 2025 사업보고서(2026.03.16), II. 사업의 내용, 4. 매출 및 수주상황. 2023~2025 매출구조. 원자료 백만원을 억원으로 환산.
- **사업 방향:** 삼진제약 코프로모션 확대 관련 사업 설명. 코프로모션 개별 계약금액·매입원가율·지급/회수일은 본 공시의 매출구조 표에서 직접 확인할 수 없으므로 모두 사용자 가정.
- **산식:** 연간 매출액을 12개월에 균등 배분; 각 월 매출을 달력상 날짜에 균등 배분; 수금일 = 발생일 + 회수일; 매입대금 지급일 = 발생일 + 지급일; 매입액 = 매출액 × 원가율.
- **필요 운전자금:** 시뮬레이션 기간 중 누적 순현금흐름의 최저값이 음수일 때 그 절댓값. 사업 초기 현금잔액 0을 가정.
- **주의:** 공시의 상품 매출은 코프로모션 매출과 일치하지 않음. 판촉·운영비·부가세·재고매입 선행·반품·수수료·세금·기존 사업현금흐름·차입금 상환·계약상 실제 결제조건 등은 제외. 실제 자금일보나 회사의 공식 예측치가 아님.''')
