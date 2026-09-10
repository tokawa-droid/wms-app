import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

st.set_page_config(page_title="倉庫基幹システム (WMS)", layout="wide")

CSV_FILE_PATH = "saved_inventory.csv"

# 初期サンプルデータ定義
DEFAULT_INVENTORY = pd.DataFrame([
    {"ロケ名": "3C-1-4-4", "商品コード": "755851", "JANコード": "4901234567891", "商品名1": "コーナン インナークッション", "引当済数": 0, "未引当数": 10, "在庫日": "2026/06/05", "品質区分名": "良品"},
    {"ロケ名": "3B-T4-2-4", "商品コード": "273386", "JANコード": "4901234567892", "商品名1": "レンジマグカップ ブラウン", "引当済数": 0, "未引当数": 163, "在庫日": "2026/06/16", "品質区分名": "良品"},
    {"ロケ名": "3B-T5-2-4", "商品コード": "121186", "JANコード": "4901234567893", "商品名1": "モデルナ IHウォックパン 20cm", "引当済数": 2, "未引当数": 69, "在庫日": "2026/06/08", "品質区分名": "良品"}
])

# 1. ログイン認証
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("📦 倉庫基幹システム (WMS)")
        st.caption("拠点: DPL草加 (GMTradings)")
        st.subheader("🔒 ログイン")
        password = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if password == "1234":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが違います")
        return False
    return True

if check_password():
    # 2. データの読み込み・保持（ファイルが存在すれば優先読み込み）
    if "inventory_db" not in st.session_state:
        if os.path.exists(CSV_FILE_PATH):
            try:
                st.session_state["inventory_db"] = pd.read_csv(CSV_FILE_PATH)
            except Exception:
                st.session_state["inventory_db"] = DEFAULT_INVENTORY
        else:
            st.session_state["inventory_db"] = DEFAULT_INVENTORY

    if "history_db" not in st.session_state:
        st.session_state["history_db"] = pd.DataFrame([
            {"日時": "2026-09-01 10:00", "区分": "入荷", "商品コード": "755851", "商品名1": "コーナン インナークッション", "数量": 10, "ロケ名": "3C-1-4-4", "担当者": "管理者"},
            {"日時": "2026-09-02 14:30", "区分": "出荷", "商品コード": "121186", "商品名1": "モデルナ IHウォックパン 20cm", "数量": 2, "ロケ名": "3B-T5-2-4", "担当者": "スタッフA"}
        ])

    if "product_master" not in st.session_state:
        st.session_state["product_master"] = pd.DataFrame([
            {"商品コード": "755851", "JANコード": "4901234567891", "商品名1": "コーナン インナークッション", "規格": "標準", "安全在庫": 5},
            {"商品コード": "273386", "JANコード": "4901234567892", "商品名1": "レンジマグカップ ブラウン", "規格": "BR", "安全在庫": 20},
            {"商品コード": "121186", "JANコード": "4901234567893", "商品名1": "モデルナ IHウォックパン 20cm", "規格": "20cm", "安全在庫": 10}
        ])

    if "loc_master" not in st.session_state:
        st.session_state["loc_master"] = pd.DataFrame([
            {"ロケ名": "3C-1-4-4", "エリア": "3C", "種別": "ピッキングロケ"},
            {"ロケ名": "3B-T4-2-4", "エリア": "3B", "種別": "保管ロケ"},
            {"ロケ名": "3B-T5-2-4", "エリア": "3B", "種別": "保管ロケ"}
        ])

    # 3. システムヘッダー ＆ メインメニュー構成
    st.title("🏭 倉庫基幹システム (WMS)")
    st.caption("拠点: DPL草加 (GMTradings)")

    menu = st.sidebar.radio(
        "📌 メインメニュー",
        ["🏠 ポータル", "🔍 在庫管理", "📋 出荷管理", "📥 入荷管理", "⚙️ マスター管理"]
    )

    # ---------------------------------------------------------
    # メニュー1: 🏠 ポータル
    # ---------------------------------------------------------
    if menu == "🏠 ポータル":
        st.subheader("📊 倉庫運用サマリー")
        inv_df = st.session_state["inventory_db"]
        
        col1, col2, col3, col4 = st.columns(4)
        sku_cnt = len(inv_df["商品コード"].unique()) if "商品コード" in inv_df.columns else 0
        free_qty = int(inv_df["未引当数"].sum()) if "未引当数" in inv_df.columns else 0
        alloc_qty = int(inv_df["引当済数"].sum()) if "引当済数" in inv_df.columns else 0
        loc_cnt = len(inv_df["ロケ名"].unique()) if "ロケ名" in inv_df.columns else 0

        col1.metric("総SKU数", sku_cnt)
        col2.metric("総フリー在庫数", free_qty)
        col3.metric("総引当済数", alloc_qty)
        col4.metric("総ロケーション数", loc_cnt)

        st.markdown("---")
        st.subheader("⚡ クイックナビゲーション")
        q_col1, q_col2, q_col3 = st.columns(3)
        with q_col1:
            st.info("🔍 **在庫詳細検索・CSV一括取り込み**\nロケや製品名での絞り込み＆在庫データ更新")
        with q_col2:
            st.success("📋 **出荷データ取り込み**\nCSV指示書からロケ順ピッキングリスト作成")
        with q_col3:
            st.warning("📥 **入荷予定・検品**\n入荷指示の受入と実在庫自動反映")

    # ---------------------------------------------------------
    # メニュー2: 🔍 在庫管理
    # ---------------------------------------------------------
    elif menu == "🔍 在庫管理":
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
            "🔎 在庫詳細検索", 
            "📥 在庫CSV一括取り込み", 
            "📜 受払履歴（入出庫追跡）", 
            "📋 棚卸（全棚・日々棚）"
        ])

        # タブ1: 在庫詳細検索
        with sub_tab1:
            st.subheader("🔍 マルチ条件 在庫詳細検索")
            df = st.session_state["inventory_db"].copy()

            with st.expander("🛠️ 詳細検索フィルター", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    src_loc = st.text_input("ロケーション名 (部分一致)", "")
                    src_code = st.text_input("商品コード", "")
                with c2:
                    src_name = st.text_input("商品名 (部分一致)", "")
                    qual_list = ["すべて"] + list(df["品質区分名"].unique()) if "品質区分名" in df.columns else ["すべて"]
                    src_qual = st.selectbox("品質区分", qual_list)
                with c3:
                    stock_flag = st.radio("在庫有無", ["すべて", "未引当ありのみ", "引当済ありのみ"], horizontal=True)

            filtered_df = df.copy()
            if src_loc and "ロケ名" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["ロケ名"].astype(str).str.contains(src_loc, case=False, na=False)]
            if src_code and "商品コード" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["商品コード"].astype(str).str.contains(src_code, case=False, na=False)]
            if src_name and "商品名1" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["商品名1"].astype(str).str.contains(src_name, case=False, na=False)]
            if src_qual != "すべて" and "品質区分名" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["品質区分名"] == src_qual]
            if stock_flag == "未引当ありのみ" and "未引当数" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["未引当数"] > 0]
            elif stock_flag == "引当済ありのみ" and "引当済数" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["引当済数"] > 0]

            st.write(f"検索結果: **{len(filtered_df)}** 件")
            st.dataframe(filtered_df, use_container_width=True)

            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 検索結果をCSVダウンロード", data=csv, file_name="inventory_search.csv", mime="text/csv")

        # タブ2: 在庫CSV一括取り込み（永続保存機能付き）
        with sub_tab2:
            st.subheader("📥 既存在庫CSVデータの取り込み（完全保存）")
            st.caption("CSVをアップロードして確定を押すと、サーバー上にファイルとして永久保存されます。")
            uploaded_file = st.file_uploader("在庫CSVファイルを選択してください", type=["csv"], key="inv_upload")
            
            if uploaded_file is not None:
                new_df = pd.read_csv(uploaded_file)
                st.write("▼ 取り込みデータのプレビュー")
                st.dataframe(new_df.head(), use_container_width=True)
                
                if st.button("💾 データベースに反映＆永久保存"):
                    # セッション更新 ＋ ローカルCSVへ書き出し
                    st.session_state["inventory_db"] = new_df
                    new_df.to_csv(CSV_FILE_PATH, index=False)
                    st.success("🎉 在庫データベースの更新および保存が完了しました！ブラウザを再読み込みしても保持されます。")

            if os.path.exists(CSV_FILE_PATH):
                if st.button("⚠️ 初期データにリセットする"):
                    if os.path.exists(CSV_FILE_PATH):
                        os.remove(CSV_FILE_PATH)
                    st.session_state["inventory_db"] = DEFAULT_INVENTORY
                    st.success("初期状態にリセットしました。")
                    st.rerun()

        # タブ3: 受払履歴
        with sub_tab3:
            st.subheader("📜 受払履歴 追跡検索")
            hist_df = st.session_state["history_db"].copy()

            hc1, hc2 = st.columns(2)
            with hc1:
                h_name = st.text_input("製品名・コードで検索", "")
            with hc2:
                h_kbn = st.selectbox("区分絞り込み", ["すべて", "入荷", "出荷", "移動", "棚卸"])

            if h_name:
                hist_df = hist_df[hist_df["商品コード"].astype(str).str.contains(h_name, case=False, na=False) | hist_df["商品名1"].astype(str).str.contains(h_name, case=False, na=False)]
            if h_kbn != "すべて":
                hist_df = hist_df[hist_df["区分"] == h_kbn]

            st.dataframe(hist_df, use_container_width=True)
            csv_h = hist_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 履歴データをCSVダウンロード", data=csv_h, file_name="history_log.csv", mime="text/csv")

        # タブ4: 棚卸
        with sub_tab4:
            st.subheader("📋 棚卸処理 (全棚 / 日々棚)")
            t_type = st.radio("棚卸種別", ["日々棚卸 (エリア・商品指定)", "全棚棚卸"], horizontal=True)
            st.info("帳簿上の実数と実カウントを入力し、差分を確定します。")
            
            show_cols = [c for c in ["ロケ名", "商品コード", "商品名1", "未引当数"] if c in st.session_state["inventory_db"].columns]
            stock_edit_df = st.data_editor(
                st.session_state["inventory_db"][show_cols],
                key="inventory_editor",
                use_container_width=True
            )
            if st.button("⚖️ 棚卸実績を確定・在庫更新"):
                st.session_state["inventory_db"]["未引当数"] = stock_edit_df["未引当数"]
                st.session_state["inventory_db"].to_csv(CSV_FILE_PATH, index=False)
                st.success("棚卸結果をデータベースに反映・保存しました！")

    # ---------------------------------------------------------
    # メニュー3: 📋 出荷管理
    # ---------------------------------------------------------
    elif menu == "📋 出荷管理":
        s_tab1, s_tab2 = st.tabs(["📥 出荷指示インポート ＆ ピッキングリスト", "🔍 出荷検索"])

        with s_tab1:
            st.subheader("📄 出荷指示CSV取り込み")
            ship_file = st.file_uploader("出荷指示CSVを選択（必須列: 商品コード, 出荷希望数）", type=["csv"])

            if ship_file is not None:
                ship_df = pd.read_csv(ship_file)
                st.write("▼ 読み込みプレビュー")
                st.dataframe(ship_df.head(), use_container_width=True)

                if st.button("⚡ ピッキングリスト（ロケーション順）生成"):
                    inv_df = st.session_state["inventory_db"].copy()
                    picking_res = []

                    qty_col = "出荷希望数" if "出荷希望数" in ship_df.columns else ("数量" if "数量" in ship_df.columns else None)

                    if qty_col is None or "商品コード" not in ship_df.columns:
                        st.error("CSV内に『商品コード』および『出荷希望数（または数量）』列が見つかりません。")
                    else:
                        for idx, row in ship_df.iterrows():
                            p_code = str(row["商品コード"])
                            req_qty = int(row[qty_col])
                            match = inv_df[inv_df["商品コード"].astype(str) == p_code]

                            if match.empty:
                                picking_res.append({"ロケ名": "【欠品】", "商品コード": p_code, "商品名1": "不明", "指示数": req_qty, "状態": "在庫なし"})
                            else:
                                for _, inv_r in match.iterrows():
                                    picking_res.append({
                                        "ロケ名": inv_r["ロケ名"], "商品コード": p_code,
                                        "商品名1": inv_r.get("商品名1", ""), "指示数": req_qty,
                                        "現在未引当": inv_r.get("未引当数", 0), "状態": "OK" if inv_r.get("未引当数", 0) >= req_qty else "不足注意"
                                    })

                        res_df = pd.DataFrame(picking_res).sort_values(by="ロケ名")
                        st.session_state["last_picking"] = res_df
                        st.success("ピッキングリストを作成しました！")

            if "last_picking" in st.session_state:
                st.markdown("---")
                st.subheader("🖨️ 生成されたピッキングリスト")
                st.dataframe(st.session_state["last_picking"], use_container_width=True)
                csv_p = st.session_state["last_picking"].to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 ピッキングリストCSV出力", data=csv_p, file_name="picking_list.csv", mime="text/csv")

        with s_tab2:
            st.subheader("🔍 出荷履歴・データ詳細検索")
            st.text_input("製品名 / 出荷IDで検索")
            st.date_input("出荷日範囲指定", (date.today(), date.today()))

    # ---------------------------------------------------------
    # メニュー4: 📥 入荷管理
    # ---------------------------------------------------------
    elif menu == "📥 入荷管理":
        r_tab1, r_tab2 = st.tabs(["📥 入荷予定インポート / 検品格納", "🔍 入荷検索"])

        with r_tab1:
            st.subheader("📦 入荷指示データの取り込み ＆ 検品格納")
            rec_file = st.file_uploader("入荷予定CSVを選択", type=["csv"], key="rec_csv")
            if rec_file is not None:
                rec_df = pd.read_csv(rec_file)
                st.dataframe(rec_df, use_container_width=True)

            st.markdown("---")
            st.subheader("📍 現場入荷検品・棚入れ（ロケ格納）")
            rc1, rc2 = st.columns(2)
            with rc1:
                in_code = st.text_input("入荷商品コード", key="in_code")
                in_qty = st.number_input("入荷数量", min_value=1, value=1)
            with rc2:
                in_loc = st.text_input("格納先ロケーション名", key="in_loc")
                in_qual = st.selectbox("品質区分", ["良品", "不良品", "保留"])

            if st.button("✅ 検品完了・在庫追加確定"):
                new_hist = pd.DataFrame([{
                    "日時": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "区分": "入荷", "商品コード": in_code, "商品名1": "入荷登録品",
                    "数量": in_qty, "ロケ名": in_loc, "担当者": "現場担当"
                }])
                st.session_state["history_db"] = pd.concat([st.session_state["history_db"], new_hist], ignore_index=True)
                st.success(f"商品コード: {in_code} を ロケ: {in_loc} に {in_qty} 個格入れ完了しました！")

        with r_tab2:
            st.subheader("🔍 入荷実績詳細検索")
            st.text_input("入荷製品名 / 仕入先で検索")
            st.date_input("入荷日範囲指定", (date.today(), date.today()))

    # ---------------------------------------------------------
    # メニュー5: ⚙️ マスター管理
    # ---------------------------------------------------------
    elif menu == "⚙️ マスター管理":
        m_tab1, m_tab2, m_tab3 = st.tabs(["📦 商品マスター", "📍 ロケーションマスター", "👤 ユーザーIDマスター"])

        with m_tab1:
            st.subheader("📦 商品マスター参照・編集")
            p_master = st.data_editor(st.session_state["product_master"], use_container_width=True)
            if st.button("保存 (商品マスター更新)"):
                st.session_state["product_master"] = p_master
                st.success("商品マスターを更新しました")

        with m_tab2:
            st.subheader("📍 ロケーションマスター参照・編集")
            l_master = st.data_editor(st.session_state["loc_master"], use_container_width=True)
            if st.button("保存 (ロケマスター更新)"):
                st.session_state["loc_master"] = l_master
                st.success("ロケーションマスターを更新しました")

        with m_tab3:
            st.subheader("👤 ユーザーID・権限マスター")
            st.dataframe(pd.DataFrame([
                {"ユーザーID": "admin", "氏名": "管理者", "権限": "フルアクセス"},
                {"ユーザーID": "staff01", "氏名": "現場担当A", "権限": "作業・検品のみ"}
            ]), use_container_width=True)
