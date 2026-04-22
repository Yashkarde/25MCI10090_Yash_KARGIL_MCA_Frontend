import React, { useState, useRef } from "react";
import "./App.css";

function App() {

  const [notes, setNotes] = useState([]);
  const [editIndex, setEditIndex] = useState(null);

  const inputRef = useRef();

  const addNote = () => {
    const text = inputRef.current.value;

    if (text === "") return;

    if (editIndex !== null) {
      const updatedNotes = [...notes];
      updatedNotes[editIndex] = text;
      setNotes(updatedNotes);
      setEditIndex(null);
    } else {
      setNotes([...notes, text]);
    }

    inputRef.current.value = "";
  };

  const deleteNote = (index) => {
    const filteredNotes = notes.filter((_, i) => i !== index);
    setNotes(filteredNotes);
  };

  const editNote = (index) => {
    inputRef.current.value = notes[index];
    setEditIndex(index);
  };

  return (
    <div className="container">

      <h2 className="title">Notes App</h2>

      <div className="inputBox">
        <input
          type="text"
          placeholder="Enter your note..."
          ref={inputRef}
        />

        <button className="addBtn" onClick={addNote}>
          Add
        </button>
      </div>

      <div className="notesContainer">
        {notes.map((note, index) => (
          <div key={index} className="noteCard">

            <span>{note}</span>

            <div className="buttons">
              <button className="editBtn" onClick={() => editNote(index)}>Edit</button>
              <button className="deleteBtn" onClick={() => deleteNote(index)}>Delete</button>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}

export default App;