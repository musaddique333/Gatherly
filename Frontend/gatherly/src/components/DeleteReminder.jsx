import React from "react";
import { IconButton } from "@mui/material";
import { Delete } from "@mui/icons-material";
import { eventAxiosInstance } from "../axiosInstance";
import Swal from 'sweetalert2';

const DeleteReminder = (props) => {
  const { reminder_id } = props;

  const handleDelete = () => {
    eventAxiosInstance.delete(`/reminder/${reminder_id}`)
      .then((response) => {
        Swal.fire({
          icon: "success",
          title: "Reminder Deleted Successfully",
          text: "Your reminder has been deleted successfully."
        }).then(() => {
          // Reload the current page
          window.location.reload();
        });
      })
      .catch((error) => {
        Swal.fire({
          icon: "error",
          title: "Error Deleting Reminder",
          text: error.response?.data?.message || "Something went wrong."
        });
      });
  };

  return (
    <IconButton onClick={handleDelete}>
      <Delete />
    </IconButton>
  );
}

export default DeleteReminder;
