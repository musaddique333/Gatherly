import PropTypes from 'prop-types';
import { Button } from '@mui/material';
import { Link } from 'react-router-dom';

// Navbar button is a stylised button with some extra link functionality
export default function NavbarButton({ to, children, ...props }) {
  return (
    <Button
      component={Link}
      to={to}
      sx={{
        margin: 2,
        fontWeight: "bold",
        position: "relative",
        color: "inherit",
        "&:after": {
          content: '""',
          position: "absolute",
          left: 0,
          bottom: 0,
          width: "100%",
          height: "2px",
          background: "currentColor",
          backgroundColor: "white",
          transform: "scaleX(0)",
          transformOrigin: "left",
          transition: "transform 250ms ease-in",
        },
        "&:hover:after": {
          transform: "scaleX(1)",
        },
      }}
      {...props}
    >
      {children}
    </Button>
  );
}

NavbarButton.propTypes = {
    to: PropTypes.string.isRequired,
    children: PropTypes.string,
}