import React from 'react';
import {BrowserRouter as Router} from 'react-router-dom';
import {
    ThemeProvider,
    CssBaseline,
} from '@material-ui/core';
import {createTheme} from '@material-ui/core/styles';
import './App.css';
import Theme from "./Theme";
import AppRoutes from "./AppRoutes";
import Content from "../common/Content";
import Header from "../common/Header";
import DataService from '../services/DataService';


const App = (props) => {

    console.log("================================== App ======================================");

    // Init Data Service
    DataService.Init();

    const darkTheme = createTheme({
        palette: {
            type: 'dark',
        },
    });

    // Build App
    let view = (
        <React.Fragment>
            <ThemeProvider theme={darkTheme}>
                <CssBaseline/>
                <Router basename="/">
                    <Header></Header>
                    <Content>
                        <AppRoutes/>
                    </Content>
                </Router>
            </ThemeProvider>
        </React.Fragment>
    )

    // Return View
    return view
}

export default App;

