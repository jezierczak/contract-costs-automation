def render_stdout(df):
    if df.empty:
        print("No data.")
        return

    print(df.to_string(index=False))
