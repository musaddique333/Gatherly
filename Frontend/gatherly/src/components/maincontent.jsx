import {styled} from "@mui/system"
import  navbarHeights  from "./navbarheights"

// Used to push content from the Navbar.
const MainContent = styled('div')(({theme})=> ({
    background: "#ffffff",
    height: navbarHeights.xs,
    [theme.breakpoints.up('sm')]: {
        paddingTop: navbarHeights.sm,
    },
    [theme.breakpoints.up('md')]: {
        paddingTop: navbarHeights.md,
    },
    [theme.breakpoints.up('lg')]: {
        paddingTop: navbarHeights.lg,
    },

}));


export default MainContent;