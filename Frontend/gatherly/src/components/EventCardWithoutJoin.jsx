import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Button } from "@mui/material";
import { Event } from "@mui/icons-material";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const EventCardWithoutJoin = ({eventdata}) => {
  const formatDate = (dateString) => new Date(dateString).toLocaleString();
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/user/add-member", { state: { eventdata} });
  };

  const {userId} = useContext(AuthContext);

  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-4">
      <div className="px-6 py-4">
        <div className="flex items-center mb-2">
          {/* Optional Icon */}
          <Event className="text-blue-500 mr-2" />
          <h2 className="font-bold text-xl text-gray-800">{eventdata.title}</h2>
        </div>
        <p className="text-gray-600 text-sm mb-2">
          📅 {formatDate(eventdata.date)}
        </p>

        <p className="text-gray-600 text-sm mb-2">
          Room Id: {eventdata.id}
        </p>
        <p className="text-gray-700 text-base mb-2">
          {eventdata.description || "No description provided."}
        </p>
        <p className="text-gray-600 text-sm mb-2">
          📍 {eventdata.isOnline ? "Online" : eventdata.location || "Location not specified."}
        </p>
        {eventdata.tags && eventdata.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {eventdata.tags.map((tag, index) => (
              <span
                key={index}
                className="bg-blue-500 text-white text-xs px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        <p className="text-gray-500 text-xs">Organizer: {eventdata.organizer_email}</p>
      </div>

      {userId === eventdata.organizer_email && (
        <div className="px-4 py-2">
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleClick}
          >
            Add member
          </Button>
        </div>
      )}
    </div>
  );
};

// Define PropTypes for the component
EventCardWithoutJoin.propTypes = {
  eventdata: PropTypes.object.isRequired
};

export default EventCardWithoutJoin;
