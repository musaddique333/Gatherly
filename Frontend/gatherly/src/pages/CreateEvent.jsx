import React, { useState } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import { Autocomplete } from "@mui/material";

import { eventAxiosInstance } from "../axiosInstance";

const EventForm = () => {
  const [formData, setFormData] = useState({
    title: "",
    date: "",
    description: "",
    location: "",
    tags: [],
    is_online: true,
    organizer_email: "",
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
    eventAxiosInstance.post("/event/", {
      params:{
        event: formData
      }
    })
    .then((response) => {
      console.log(response);
    })
    .catch((error) => {
      console.error(error);
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

      <TextField
        label="Organizer Email"
        name="organizer_email"
        type="email"
        value={formData.organizer_email}
        onChange={handleChange}
        required
        fullWidth
      />

      <Button
        type="submit"
        variant="contained"
        color="primary"
        className="mt-4"
        onClick={handleSubmit}
      >
        Create Event
      </Button>
    </form>
  );
};

export default EventForm;
