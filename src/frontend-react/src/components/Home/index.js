import React, { useEffect, useRef, useState } from 'react';
import { withStyles } from '@material-ui/core';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import DateTimePicker from 'react-datetime-picker';
import Button from '@material-ui/core/Button';
import Plot from 'react-plotly.js';
import DataService from "../../services/DataService";
import styles from './styles';


const Home = (props) => {
    const { classes } = props;

    console.log("================================== Home ======================================");

    const inputFile = useRef(null);

    // Component States (variables and data)
    const [pair, setPair] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [date, setDate] = useState(new Date());
    const [data, setData] = useState([]);
    const [layout, setLayout] = useState({});

    // Setup Component
    useEffect(() => {

    }, []);

    // Handlers
    const handlePairChange = (event) => {
        setPair(event.target.value)
    }

    const handleDateChange = (date) => {
        setDate(date);
    }

    const handleButtonClick = () => {
        DataService.Predict({'ticker': pair, 'time': date })
        .then(function (response) {
            console.log(response.data);
            setPrediction(response.data);
            
            const dates = [];
            const lows = [];
            const highs = [];
            let maxDate = '0000-00-00';
            let minDate = '9999-99-99';

            for (let i of response.data.history) {
                dates.push(i.date);
                lows.push(i.low);
                highs.push(i.high);
                if (i.date > maxDate) 
                    maxDate = i.date;
                
                if (i.date < minDate)
                    minDate = i.date;
            }

            // set Data and Layout
            // plot
            const trace1 = {
                type: "scatter",
                mode: "lines",
                name: 'High',
                x: dates,
                y: highs,
                line: {color: '#17BECF'}
            }
            
            const trace2 = {
                type: "scatter",
                mode: "lines",
                name: 'Low',
                x: dates,
                y: lows,
                line: {color: '#7F7F7F'}
            }
            
            setData([trace1,trace2]);
            
            setLayout({
                left: "50%",
                title: 'Time Series Historical Price with Rangeslider',
                xaxis: {
                    autorange: true,
                    //range: [minDate, maxDate],
                    rangeselector: {buttons: [
                        {
                            count: 1,
                            label: '1m',
                            step: 'month',
                            stepmode: 'backward'
                        },
                        {
                            count: 6,
                            label: '6m',
                            step: 'month',
                            stepmode: 'backward'
                        },
                        {step: 'all'}
                        ]},
                    rangeslider: {range: [minDate, maxDate]},
                    type: 'date'
                },
                yaxis: {
                    autorange: true,
                    //range: [86.8700008333, 138.870004167],
                    type: 'linear'
                },
            });
        })
    };


    

    return (
        <div className={classes.root}>
            <main className={classes.main}>
                <Container className={classes.container}>
                <Typography variant="h4"  gutterBottom>
                        Plot
                    </Typography>
                    <div>
                        <Plot
                            data={ data }
                            layout={ layout}
                        />
                    </div>

                    <Typography variant="h4"  gutterBottom>
                        Prediction
                    </Typography>

                    <FormControl fullWidth={true} variant="outlined" className={classes.formControl}>
                        <InputLabel id="demo-simple-select-outlined-label">Select a pair</InputLabel>
                        <Select
                            labelId="demo-simple-select-outlined-label"
                            id="demo-simple-select-outlined"
                            value={pair}
                            onChange={handlePairChange}
                            label="pair"
                        >
                        <MenuItem value="">
                            <em>Select</em>
                        </MenuItem>
                        <MenuItem value={'BTCUSDT'}>BTCUSDT</MenuItem>
                        <MenuItem value={'BTCETH'}>BTCETH</MenuItem>
                        </Select>
                    </FormControl>

                    <div className={classes.spacer}></div>
                    <div>
                    <DateTimePicker
                        onChange={handleDateChange}
                        value={date}
                    />
                    </div>

                    <div className={classes.spacer}></div>

                    <Button onClick={handleButtonClick} variant="contained" color="primary">
                        Predict
                    </Button>
                    
                    <div className={classes.spacer}></div>

                    <Typography variant="h4"  gutterBottom>
                        Prediction Result:
                    </Typography>

                    {/* This is saying that if prediction is null, then ignore; if there is a prediction value, then display */}
                    {prediction && 
                        <Typography>
                            {prediction['prediction']}
                        </Typography>
                    }
                    
                </Container>

            </main>
        </div>
    );
};

export default withStyles(styles)(Home);