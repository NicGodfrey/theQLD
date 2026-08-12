if __name__ == "__main__":
    import uvicorn

    from sol_pool.app import create_app

    uvicorn.run(create_app(), host="0.0.0.0", port=8787)
