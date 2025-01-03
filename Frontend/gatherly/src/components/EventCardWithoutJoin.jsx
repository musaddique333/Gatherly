import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Button } from "@mui/material";
import { Event } from "@mui/icons-material";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import DeleteEvent from "./DeleteEvent";
import Swal from 'sweetalert2';

const EventCardWithoutJoin = ({ eventdata }) => {
  const formatDate = (dateString) => new Date(dateString).toLocaleString();
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/user/add-member", { state: { eventdata } });
  };

  const { userId } = useContext(AuthContext);

  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg bg-white m-4">
      <div className="px-4 py-4">
        <div className="flex items-center mb-2">
          {/* Optional Icon */}
          <Event className="text-blue-500 mr-2" />
          <h2 className="font-bold text-xl text-gray-800">{eventdata.title}</h2>
        </div>
        <p className="text-gray-600 text-sm mb-2">
          📅 {formatDate(eventdata.date)}
        </p>

        <p className="text-gray-600 text-sm mb-2">
          <span>Room Id: </span>
          <span
            className="cursor-pointer hover:text-red-600 relative group bg-red-100 hover:bg-red-200 p-1 rounded"
            style={{ whiteSpace: 'nowrap' }}
            onClick={() => {
              navigator.clipboard.writeText(eventdata.id).then(() => {
                Swal.fire({
                  icon: "success",
                  title: "Copied to clipboard",
                  showConfirmButton: false,
                  timer: 1500
                });
              });
            }}
          >
            {eventdata.id}
            <span className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 text-sm bg-gray-700 text-white p-1 rounded transition-opacity">
              Click to copy
            </span>
          </span>
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
        <p className="text-gray-500 text-xs">Organizer: {eventdata.username}</p>
      </div>

      {userId === eventdata.organizer_email && (
        <div className="px-4 py-2 flex justify-between">
          <Button
            variant="contained"
            color="primary"
            style={{ flex: '0 0 80%' }}
            onClick={handleClick}
          >
            Add member
          </Button>
          <DeleteEvent id={eventdata.id} user_email={eventdata.organizer_email} />
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
