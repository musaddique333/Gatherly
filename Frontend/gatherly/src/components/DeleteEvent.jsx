import React from "react";
import { IconButton } from "@mui/material";
import { Delete } from "@mui/icons-material";
import { eventAxiosInstance } from "../axiosInstance";
import { useLocation, useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';


const DeleteEvent = ({ id, user_email }) => {
  const navigate = useNavigate();
  const handleDelete = () => {
    eventAxiosInstance.delete(`/event/${id}`, {
      params: {
        user_email: user_email,
      }
    })
      .then((response) => {
        Swal.fire({
          icon: "success",
          title: "Event Deleted Successfully",
          text: "Your Event has been deleted successfully."
        }).then(() => {
          // Reload the current page
          window.location.reload();
        });
      })
      .catch((error) => {
        Swal.fire({
          icon: "error",
          title: "Error Deleting Event",
          text: error.response?.data?.message || "Something went wrong."
        });
      });
  }
  return (
    <IconButton onClick={handleDelete}>
      <Delete />
    </IconButton>
  )
}

export default DeleteEvent;
