import './App.css';
import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { TiDelete } from 'react-icons/ti';

const Budget = () => {
    return (
        <div className='alert alert-warning'>
            <span> Budget: $1000</span>
        </div>
    )
}
const Remaining = () => {
    return (
        <div className='alert alert-success'>
            <span> Remaining : $500</span>
        </div>
    )
}
const Total = () => {
    return (
        <div className='alert alert-danger'>
            <span> Spent so far : $500</span>
        </div>
    )
}
const ExpenseItem = (props) => {
    return (
        <li>
            {props.name}{' '}
            <span>
                ${props.cost}{' '}
            </span>
            <TiDelete size='1.5em'></TiDelete>
        </li>
    )
}
const ExpenseList = () => {
    const expenses = [
        { id: 1231232, name: "Grocery", cost: 150 },
        { id: 1231232, name: "Movie", cost: 50 },
        { id: 1231232, name: "Gas", cost: 40 },
        { id: 1231232, name: "Holiday", cost: 260 },
    ];
    return (
        <ul className="expenses-list">
            {expenses.map(((expenses) => (
                <ExpenseItem
                    id={expenses.id}
                    name={expenses.name}
                    cost={expenses.cost} />
            )))}
        </ul>
    )
}
const AddExpenseForm = () => {
    return (
        <form>
            <label for='name'>Name</label>
            <input
                required='required'
                type='text'
                id='name'>
            </input>
            <div>
                <label for='Cost'>Cost</label>
                <input
                    required='required'
                    type='text'
                    id='cost'>
                </input>
            </div>
            <div>
                <button type='submit'>
                    Save
                </button>
            </div>
        </form>
    )
}
const App = () => {
    return (
        <div>
            <h1>My Budget Planner</h1>
            <div>
                <div className='col-sm'>
                    <Budget />
                </div>
                <div className='col-sm'>
                    <Remaining />
                </div>
                <div className='col-sm'>
                    <Total />
                </div>
            </div>
            <h3>Expenses</h3>
            <div>
                <ExpenseList />
            </div>
            <h3>Add Expense</h3>
            <div>
                <AddExpenseForm />
            </div>
        </div>
    );
};


export default App;
