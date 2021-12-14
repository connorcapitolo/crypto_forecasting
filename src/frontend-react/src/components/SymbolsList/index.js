import React, { useEffect, useRef, useState } from 'react';
import { withStyles } from '@material-ui/core';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import NumberFormat from "react-number-format";

import DataService from "../../services/DataService";
import { styles, StyledTableRow, StyledTableCell } from './styles';



const SymbolsList = (props) => {
    const { classes } = props;
    let { display } = props;
    let { hideColumns } = props;

    console.log("================================== SymbolsList ======================================");


    // Component States
    const [symbols, setSymbols] = useState([]);

    // Setup Component
    useEffect(() => {
        var list = [
            { "symbol": "BTC-USD", "name": "Bitcoin USD", "price": 54439.70, "change": -289.85, "change_pct": -0.50, "mkt_cap": "1.028T", "volume": "24.561B" },
            { "symbol": "ETH-USD", "name": "Ethereum USD", "price": 4076.82, "change": -51.30, "change_pct": -1.24, "mkt_cap": "484.167B", "volume": "13.159B" },
            { "symbol": "BNB-USD", "name": "BinanceCoin USD", "price": 594.09, "change": -15.54, "change_pct": -2.55, "mkt_cap": "99.094B", "volume": "2.61B" },
            { "symbol": "USDT-USD", "name": "Tether USD", "price": 1.0013, "change": 0.0007, "change_pct": 0.0728, "mkt_cap": "73.213B", "volume": "66.278B" },
            { "symbol": "SOL1-USD", "name": "Solana USD", "price": 189.90, "change": -7.09, "change_pct": -3.60, "mkt_cap": "57.675B", "volume": "1.484B" },
            { "symbol": "ADA-USD", "name": "Cardano USD", "price": 1.5031, "change": -0.0707, "change_pct": -4.4917, "mkt_cap": "50.074B", "volume": "1.548B" },
            { "symbol": "XRP-USD", "name": "XRP USD", "price": 0.928200, "change": -0.031100, "change_pct": -3.247, "mkt_cap": "43.748B", "volume": "2.213B" },
            { "symbol": "USDC-USD", "name": "USDCoin USD", "price": 1.0002, "change": 0.0003, "change_pct": 0.0275, "mkt_cap": "38.304B", "volume": "3.575B" },
            { "symbol": "DOT1-USD", "name": "Polkadot USD", "price": 33.93, "change": -1.70, "change_pct": -4.78, "mkt_cap": "33.512B", "volume": "1.247B" }
        ];

        if (display) {
            list = list.slice(0, display);
        }

        setSymbols(list)
    }, []);

    // Handlers



    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <StyledTableRow>
                        <StyledTableCell>Symbol</StyledTableCell>
                        <StyledTableCell>Name</StyledTableCell>
                        <StyledTableCell>Price</StyledTableCell>
                        {!hideColumns &&
                            <StyledTableCell>Price Change</StyledTableCell>
                        }
                        <StyledTableCell>Price Change(%)</StyledTableCell>
                        {!hideColumns &&
                            <StyledTableCell>Market Cap</StyledTableCell>
                        }
                        {!hideColumns &&
                            <StyledTableCell>Volume</StyledTableCell>
                        }
                    </StyledTableRow>
                </TableHead>
                <TableBody>
                    {symbols && symbols.map((itm, idx) =>
                        <StyledTableRow key={idx}>
                            <StyledTableCell className={classes.tableCellSymbol}>{itm.symbol}</StyledTableCell>
                            <StyledTableCell>{itm.name}</StyledTableCell>
                            <StyledTableCell>
                                <NumberFormat
                                    value={itm.price}
                                    displayType="text"
                                    thousandSeparator={true}
                                />
                            </StyledTableCell>
                            {!hideColumns &&
                                <StyledTableCell>
                                    <NumberFormat
                                        value={itm.change}
                                        displayType="text"
                                        decimalSeparator="."
                                        decimalScale={2}
                                    />
                                </StyledTableCell>
                            }
                            <StyledTableCell>
                                <NumberFormat
                                    value={itm.change_pct}
                                    displayType="text"
                                    decimalSeparator="."
                                    decimalScale={2}
                                    suffix="%"

                                />
                            </StyledTableCell>
                            {!hideColumns && <StyledTableCell>{itm.mkt_cap}</StyledTableCell>}
                            {!hideColumns && <StyledTableCell>{itm.volume}</StyledTableCell>}
                        </StyledTableRow>
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default withStyles(styles)(SymbolsList);