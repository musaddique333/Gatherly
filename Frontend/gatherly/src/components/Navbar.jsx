import { useState, useContext } from "react";
import { AppBar, Toolbar, IconButton, Typography, Box, Menu, MenuItem } from "@mui/material";
import PeopleOutlineIcon from '@mui/icons-material/PeopleOutline';
import { useNavigate } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import NavbarButton from './navbarbutton';
import navbarHeights from './navbarheights';
import constants from './../constant';
import { useTheme } from '@mui/system';

import { AuthContext } from "../context/AuthContext";

const Navbar = () => {
  const theme = useTheme()
  const navigate = useNavigate();
  const [anchorNav, setAnchorNav] = useState(null);
  const {token, logout} = useContext(AuthContext);


  const handleOnClick = () => {
    navigate('/');
  };

  const handleMenuOpen = (event) => {
    setAnchorNav(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorNav(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const desktopStyle = {
    margin: 2,
    fontWeight: 'bold',
    position: 'relative',
    color: 'white',
    '&:after': {
      content: '""',
      position: 'absolute',
      left: 0,
      bottom: 0,
      width: '100%',
      height: '2px',
      background: 'currentColor',
      backgroundColor: 'white',
      transform: 'scaleX(0)',
      transformOrigin: 'left',
      transition: 'transform 250ms ease-in',
    },
    '&:hover:after': {
      transform: 'scaleX(1)',
    }
  };

  const mobileStyle = {
    padding: '1px 1px 1px 18px',
    width: "100%",
    color:"black",
    textTransform: 'none',
    fontWeight: 500,
    fontFamily:"Roboto",
     fontSize: 14,
     textAlign: 'left',
     display: 'block',
    marginLeft: '0',

    '&:hover': {
      backgroundColor: 'lightgrey'
  }
  }
  
  return (
    <AppBar
      position="fixed"
      sx={{
        backgroundColor: '#0D1B2A',
        height: {
          xs: navbarHeights.xs,
          sm: navbarHeights.sm,
          md: navbarHeights.md,
          lg: navbarHeights.lg,
        },
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ display: 'flex' }}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="logo"
          sx={{ alignItems: 'center' }}
          onClick={handleOnClick}
        >
          <PeopleOutlineIcon />
        </IconButton>
        <Typography
          variant="h3"
          component="div"
          sx={{
            flexGrow: 1,
            display: { md: 'flex' },
          }}
        >
          Gatherly
        </Typography>
        <Box sx={{ display: { xs: 'none', md: 'block' } }}>
          <NavbarButton to="/">{constants.general.home}</NavbarButton>
          <NavbarButton to = "/user/dashboard">User Dashboard</NavbarButton>
          <NavbarButton to="/video">{constants.general.Video}</NavbarButton>
          {token ? (
            <NavbarButton onClick={handleLogout}>{constants.general.logout}</NavbarButton>
          ) : (
            <NavbarButton to="/login">{constants.general.login_register}</NavbarButton>
          )}
        </Box>

        <IconButton
          edge="end"
          color="inherit"
          aria-label="menu"
          size="large"
          onClick={handleMenuOpen}
          sx={{ display: { xs: 'block', md: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Menu
          anchorEl={anchorNav}
          open={Boolean(anchorNav)}
          onClose={handleCloseMenu}
        >
          <MenuItem onClick={() => { handleCloseMenu(); navigate('/'); }}>{constants.general.home}</MenuItem>
          <MenuItem onClick={() => { handleCloseMenu(); navigate('/video'); }}>{constants.general.Video}</MenuItem>
          <MenuItem onClick={() => { handleCloseMenu(); navigate('/user/dashboard'); }}>User Dashboard</MenuItem>
          {token ? (
            <MenuItem onClick={() => { handleCloseMenu(); handleLogout(); }}>{constants.general.logout}</MenuItem>
          ) : (
            <MenuItem onClick={() => { handleCloseMenu(); navigate('/login'); }}>{constants.general.login_register}</MenuItem>
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
