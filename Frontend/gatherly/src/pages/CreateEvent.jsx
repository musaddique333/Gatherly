import { AuthContext } from "../context/AuthContext";
import React, { useState, useContext } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { Autocomplete } from "@mui/material";
import Swal from 'sweetalert2';
import { eventAxiosInstance } from "../axiosInstance";

const EventForm = () => {
  const { userId } = useContext(AuthContext);

  const [formData, setFormData] = useState({
    title: "",
    date: "",
    description: "",
    location: "",
    tags: [],
    is_online: true,
    organizer_email: userId,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleCheckboxChange = (e) => {
    setFormData({
      ...formData,
      is_online: e.target.checked,
    });
  };

  const handleTagsChange = (event, value) => {
    setFormData({
      ...formData,
      tags: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Convert date to ISO format before sending it to the server
    const formattedDate = new Date(formData.date).toISOString();
  
    const eventData = {
      ...formData,
      date: formattedDate,
    };
  
    // Send the event data to the backend
    eventAxiosInstance
      .post("/event/", eventData)
      .then((response) => {
        // Show success message with SweetAlert
        Swal.fire({
          icon: "success",
          title: "Event Created Successfully",
          text: "Your event has been successfully created and added.",
        });
      })
      .catch((error) => {
        // Show error message with SweetAlert
        Swal.fire({
          icon: "error",
          title: "Event Creation Failed",
          text: error.response?.data?.message || "Something went wrong.",
        });
      });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-4 max-w-lg mx-auto bg-white shadow-md rounded-lg"
    >
      <TextField
        label="Title"
        name="title"
        value={formData.title}
        onChange={handleChange}
        required
        fullWidth
      />

      <TextField
        label="Date"
        name="date"
        type="datetime-local"
        value={formData.date}
        onChange={handleChange}
        required
        InputLabelProps={{ shrink: true }}
        fullWidth
      />

      <TextField
        label="Description"
        name="description"
        value={formData.description}
        onChange={handleChange}
        multiline
        rows={4}
        fullWidth
      />

      <TextField
        label="Location"
        name="location"
        value={formData.location}
        onChange={handleChange}
        fullWidth
      />

      <Autocomplete
        multiple
        options={[]}
        freeSolo
        onChange={handleTagsChange}
        renderInput={(params) => (
          <TextField {...params} label="Tags" placeholder="Add tags" />
        )}
      />

      <FormControlLabel
        control={
          <Checkbox
            checked={formData.is_online}
            onChange={handleCheckboxChange}
          />
        }
        label="Is Online?"
      />

      <Button
        type="submit"
        variant="contained"
        color="primary"
        className="mt-4"
      >
        Create Event
      </Button>
    </form>
  );
};

export default EventForm;
