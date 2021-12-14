import React, { useEffect, useRef, useState } from 'react';
import { withStyles } from '@material-ui/core';
import Container from '@material-ui/core/Container';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';

import DataService from "../../services/DataService";
import styles from './styles';
import SymbolsList from '../SymbolsList';


const Symbols = (props) => {
    const { classes } = props;

    console.log("================================== Symbols ======================================");


    // Component States


    // Setup Component
    useEffect(() => {

    }, []);

    // Handlers


    return (
        <div className={classes.root}>
            <main className={classes.main}>
                <Container maxWidth="lg" className={classes.container}>
                    <Toolbar className={classes.toolBar}>
                        <Typography variant="h5" display="block" gutterBottom={false}>
                            Cryptocurrencies
                        </Typography>
                        <div className={classes.grow} />
                        <Typography variant="caption" display="block" gutterBottom={false}>
                            Pricing data is updated frequently. Currency in USD
                        </Typography>
                    </Toolbar>
                    <Divider />
                    <div className={classes.spacer}></div>
                    <SymbolsList></SymbolsList>
                </Container>
            </main>
        </div>
    );
};

export default withStyles(styles)(Symbols);