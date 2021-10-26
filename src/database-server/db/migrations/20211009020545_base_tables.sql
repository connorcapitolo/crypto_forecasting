-- migrate:up
CREATE TABLE symbols (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM clock_timestamp()) * 1000,
    updated_at BIGINT
);
CREATE UNIQUE INDEX symbols_name_index ON symbols (name);
CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    symbol_id BIGINT NOT NULL REFERENCES symbols ON DELETE CASCADE,
    open_time BIGINT NOT NULL,
    open_price NUMERIC NOT NULL,
    high_price NUMERIC NOT NULL,
    low_price NUMERIC NOT NULL,
    close_price NUMERIC NOT NULL,
    volume_traded NUMERIC NOT NULL,
    close_time BIGINT NOT NULL,
    quote_asset_volume NUMERIC NOT NULL,
    number_of_trades INT NOT NULL,
    taker_buy_base_asset_volume NUMERIC NOT NULL,
    taker_buy_quote_asset_volume NUMERIC NOT NULL,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM clock_timestamp()) * 1000,
    updated_at BIGINT
);
--CREATE UNIQUE INDEX price_history_symbol_open_time ON price_history (symbol_id, open_time);

-- migrate:down
DROP TABLE IF EXISTS price_history;
DROP TABLE IF EXISTS symbols;

