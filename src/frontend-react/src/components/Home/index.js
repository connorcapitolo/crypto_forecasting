import React, { useState, useEffect } from 'react';
import {
    Grid,
    ListItem,
    ListItemText,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    withStyles
} from '@material-ui/core';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import DarkUnica from 'highcharts/themes/dark-unica';
import Highcharts from 'highcharts'
import DataService from "../../services/DataService";
import { styles, StyledTableRow, StyledTableCell } from './styles';
import List from "@material-ui/core/List";
import HighchartsReact from "highcharts-react-official";
import NumberFormat from "react-number-format";

const Home = (props) => {
    const { classes } = props;

    DarkUnica(Highcharts);

    console.log("================================== Home ======================================");

    const generateOptions = function (name, historyData, predictionData) {
        const data = [];
        data.push(...historyData);
        data.push(...predictionData);

        const colorOptions = function (idx) {
            return {
                color: Highcharts.getOptions().colors[idx],
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[idx]],
                        [1, Highcharts.color(Highcharts.getOptions().colors[idx]).setOpacity(0).get('rgba')]
                    ]
                },
            }
        }

        const opt = {
            legend: { enabled: false },
            credits: { enabled: false },
            chart: {
                zoomType: 'x',
            },
            xAxis: {
                type: 'datetime',
            },
            yAxis: {
                title: { text: name },
            },
            title: { text: 'History & Future' },
            subtitle: {
                text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            plotOptions: { area: { threshold: null } },
            time: { useUTC: false },
            series: [{
                type: 'area',
                name: name,
                data: data,
                zoneAxis: 'x',
                zones: (predictionData.length === 0 || historyData.length === 0) ? [] : [
                    {
                        value: new Date(predictionData[0].x.getTime() + historyData[historyData.length - 1].x.getTime()) / 2,
                        ...colorOptions(0),
                    },
                    {
                        ...colorOptions(2),
                    },
                ],
            }]
        };
        console.log(opt);
        return opt;
    }

    const [options, setOptions] = useState(generateOptions('', [], []));
    const [rows, setRows] = useState([]);

    const onListClick = function (symbol) {
        DataService.Predict({ 'symbol': symbol })
            .then(function (response) {
                console.log(response.data);

                const historyData = [];
                const predictionData = [];
                for (const point of response.data.history) {
                    historyData.push({
                        x: new Date(point['close_time']),
                        y: point['close_price'],
                    });
                }
                for (const point of response.data.prediction) {
                    predictionData.push({
                        x: new Date(point['close_time']),
                        y: point['close_price'],
                    });
                }

                setOptions(generateOptions(symbol, historyData, predictionData));

                const r = [];
                for (const idx of [0, 1, 5, 10, 15, 30]) {
                    const p = response.data.prediction[idx];
                    const date = new Date(p['close_time']);
                    r.push({
                        time: `${date.toLocaleTimeString()} (+${idx} min)`,
                        price: p['close_price'],
                    });
                }
                setRows(r);
            })
    }

    const [currentData, setCurrentData] = useState([]);
    const loadCurrentData = () => {
        DataService.GetCurrentTopOfBookData()
            .then(function (response) {
                setCurrentData(response.data);
            })
    }

    const symbols = ['BTCUSDT', 'ETHBTC', 'BNBBTC', 'BNBUSDT', 'ETHUSDT'];
    const listItem = function (symbol) {
        return <ListItem button>
            <ListItemText primary={symbol} onClick={() => {
                onListClick(symbol)
            }} />
        </ListItem>
    }

    // Setup Component
    useEffect(() => {

        // setInterval
        // this is querying the API every 5 seconds to update the top_of_book
        const timeout = setInterval(() => {
            loadCurrentData();
        }, 5000);

        return () => clearInterval(timeout);
    }, []);

    return <div className={classes.root}>
        <Container>
            <Grid container spacing={3}>
                <Grid item xs={3}>
                    <List component="nav">
                        {symbols.map(listItem)}
                    </List>
                    <br />

                </Grid>
                <Grid item xs={9}>
                    <Typography variant="h4" gutterBottom>
                        <br></br>
                        Visualization Plot
                    </Typography>

                    <div style={{ width: '900px' }} >
                        <HighchartsReact highcharts={Highcharts} options={options} />
                    </div>



                </Grid>
            </Grid>
            <Grid container spacing={3}>
                <Grid item md={6}>
                    <Typography variant="h5" display="block" gutterBottom={false}>
                        Live Market Data
                    </Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <StyledTableRow>
                                    <StyledTableCell>Symbol</StyledTableCell>
                                    <StyledTableCell>Best Bid</StyledTableCell>
                                    <StyledTableCell>Best Bid(Volume)</StyledTableCell>
                                    <StyledTableCell>Best Ask</StyledTableCell>
                                    <StyledTableCell>Best Ask(Volume)</StyledTableCell>
                                </StyledTableRow>
                            </TableHead>
                            <TableBody>
                                {currentData && currentData.map((itm, idx) =>
                                    <StyledTableRow key={idx}>
                                        <StyledTableCell className={classes.tableCellSymbol}>{itm.name}</StyledTableCell>
                                        <StyledTableCell>
                                            <NumberFormat
                                                value={itm.best_bid}
                                                displayType="text"
                                                thousandSeparator={true}
                                            />
                                        </StyledTableCell>
                                        <StyledTableCell>
                                            <NumberFormat
                                                value={itm.volume_best_bid}
                                                displayType="text"
                                                thousandSeparator={true}
                                            />
                                        </StyledTableCell>
                                        <StyledTableCell>
                                            <NumberFormat
                                                value={itm.best_ask}
                                                displayType="text"
                                                thousandSeparator={true}
                                            />
                                        </StyledTableCell>
                                        <StyledTableCell>
                                            <NumberFormat
                                                value={itm.volume_best_ask}
                                                displayType="text"
                                                thousandSeparator={true}
                                            />
                                        </StyledTableCell>
                                    </StyledTableRow>
                                )}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Grid>
                <Grid item md={6}>
                    <Typography variant="h4" gutterBottom>
                        <br></br>
                        Prediction Results
                    </Typography>

                    <TableContainer>
                        <Table className={classes.table}>
                            <TableHead>
                                <TableRow>
                                    <TableCell><b>Time (Local Timezone)</b></TableCell>
                                    <TableCell><b>Predicted Price</b></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.map((row) => (
                                    <TableRow key={row.time}>
                                        <TableCell component="th" scope="row">
                                            {row.time}
                                        </TableCell>
                                        <TableCell align="left">{row.price.toFixed(6)}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Grid>
            </Grid>
        </Container>
    </div>;
};

export default withStyles(styles)(Home);