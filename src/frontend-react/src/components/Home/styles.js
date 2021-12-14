import { withStyles } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';

export const styles = theme => ({
    // root: {
    //     flexGrow: 1,
    // },
    // grow: {
    //     flexGrow: 1,
    // },
    // main: {
    //
    // },
    // container: {
    //     paddingTop: "10px",
    // },
    // spacer: {
    //     padding: "10px",
    // },
    // toolBar: {
    //     paddingLeft: "0px",
    //     paddingRight: "0px",
    //     minHeight: "0px",
    // },
    // symbolFormControl: {
    //     // margin: theme.spacing(1),
    //     minWidth: 200,
    // },
});

export const StyledTableCell = withStyles((theme) => ({
    head: {
        backgroundColor: theme.palette.common.black,
        color: theme.palette.common.white,
        fontSize: "0.80rem",
        lineHeight: "1.0rem",
    },
    body: {
        fontSize: "0.80rem",
        lineHeight: "1.0rem",
    },
}))(TableCell);

export const StyledTableRow = withStyles((theme) => ({
    root: {
        '&:nth-of-type(odd)': {
            backgroundColor: theme.palette.action.hover,
        },
    },
}))(TableRow);

export default styles;