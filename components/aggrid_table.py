from st_aggrid import AgGrid, GridOptionsBuilder


def mostrar_aggrid(df):

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        sortable=True,
        filter=True,
        resizable=True,
    )

    if "ID" in df.columns:
        gb.configure_column(
            "ID",
            hide=True,
        )

    gb.configure_selection(
        selection_mode="single",
        use_checkbox=True,
    )

    gb.configure_pagination(
        enabled=True,
        paginationAutoPageSize=False,
        paginationPageSize=10,
    )

    return AgGrid(
        df,
        gridOptions=gb.build(),
        fit_columns_on_grid_load=True,
        height=400,
        theme="streamlit",
    )
