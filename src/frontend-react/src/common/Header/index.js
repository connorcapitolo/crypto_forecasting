import React, {useState} from 'react';
import {withStyles} from '@material-ui/core';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Drawer from '@material-ui/core/Drawer';
import Typography from '@material-ui/core/Typography';


import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import IconButton from '@material-ui/core/IconButton';
import AccountCircle from '@material-ui/icons/AccountCircle';
import MenuIcon from '@material-ui/icons/Menu';
import Icon from '@material-ui/core/Icon';
import {Link} from 'react-router-dom';


import styles from './styles';
import Button from "@material-ui/core/Button";

const Header = (props) => {
    const {classes} = props;

    console.log("================================== Header ======================================");


    // State
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);
    const [settingsMenuAnchorEl, setSettingsMenuAnchorEl] = useState(null);

    const toggleDrawer = (open) => () => {
        setDrawerOpen(open)
    };
    const openSettingsMenu = (event) => {
        setSettingsMenuAnchorEl(event.currentTarget);
    };
    const closeSettingsMenu = (event) => {
        setSettingsMenuAnchorEl(null);
    };

    return (
        <div className={classes.root}>
            <AppBar position="static" elevation={0} className={classes.appBar} color="default">
                <Toolbar variant="dense">
                    <IconButton className={classes.menuButton} aria-label="Menu" onClick={toggleDrawer(true)}>
                        <MenuIcon/>
                    </IconButton>
                    <Typography className={classes.title} variant="h6" noWrap>
                        💵 Crypto Forecasting
                    </Typography>
                    <Button
                        className={classes.button}
                        startIcon={<Icon>home</Icon>}
                        component={Link} to="/">
                        Home
                    </Button>
                    <Button
                        className={classes.button}
                        startIcon={<Icon>currency_exchange</Icon>}
                        component={Link} to="/symbols">
                        Symbols
                    </Button>
                </Toolbar>
            </AppBar>
            <Drawer open={drawerOpen} onClose={toggleDrawer(false)}>
                <div
                    tabIndex={0}
                    role="button"
                    onClick={toggleDrawer(false)}
                    onKeyDown={toggleDrawer(false)}
                >
                    <div className={classes.list}>
                        <List>
                            <ListItem button key='home' component={Link} to="/">
                                <ListItemIcon><Icon>home</Icon></ListItemIcon>
                                <ListItemText primary='Home'/>
                            </ListItem>
                        </List>
                        <Divider/>
                        <List>
                            <ListItem button key='menuitem12' component={Link} to="/symbols">
                                <ListItemIcon><Icon>currency_exchange</Icon></ListItemIcon>
                                <ListItemText primary='Symbols'/>
                            </ListItem>
                        </List>
                    </div>
                </div>
            </Drawer>
        </div>
    );
}

export default withStyles(styles)(Header);
