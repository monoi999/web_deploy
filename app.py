from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).with_name("score.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
	df = pd.read_csv(DATA_PATH, encoding="cp949")
	df["반"] = df["반"].astype(str)
	df["평균"] = pd.to_numeric(df["평균"], errors="coerce")
	df["결시생"] = df["평균"].fillna(0).eq(0)
	return df


def main() -> None:
	st.set_page_config(page_title="성적 데이터 필터", layout="wide")
	st.title("성적 데이터 필터링")

	df = load_data()

	class_options = sorted(df["반"].dropna().unique().tolist(), key=int)
	grade_options = sorted(df["등급"].dropna().unique().tolist())
	min_score = float(df["평균"].min())
	max_score = float(df["평균"].max())

	with st.sidebar:
		st.header("필터")
		st.subheader("반 선택")
		selected_classes = [
			class_name
			for class_name in class_options
			if st.checkbox(f"{class_name}반", value=True, key=f"class_{class_name}")
		]
		selected_grades = st.multiselect(
			"등급 선택",
			options=grade_options,
			default=grade_options,
		)
		include_absent = st.radio(
			"결시생 포함 여부",
			options=["포함", "제외"],
			index=0,
			horizontal=True,
		)
		selected_score_range = st.slider(
			"평균 점수 범위",
			min_value=min_score,
			max_value=max_score,
			value=(min_score, max_score),
			step=0.01,
		)

	filtered_df = df.copy()

	if selected_classes:
		filtered_df = filtered_df[filtered_df["반"].isin(selected_classes)]
	else:
		filtered_df = filtered_df.iloc[0:0]

	if selected_grades:
		filtered_df = filtered_df[filtered_df["등급"].isin(selected_grades)]
	else:
		filtered_df = filtered_df.iloc[0:0]

	filtered_df = filtered_df[
		filtered_df["평균"].between(selected_score_range[0], selected_score_range[1])
	]

	if include_absent == "제외":
		filtered_df = filtered_df[~filtered_df["결시생"]]

	st.subheader("필터링 결과")
	st.dataframe(
		filtered_df.drop(columns=["결시생"]),
		use_container_width=True,
		hide_index=True,
	)
	st.caption(f"조회 건수: {len(filtered_df)}명")


if __name__ == "__main__":
	main()
