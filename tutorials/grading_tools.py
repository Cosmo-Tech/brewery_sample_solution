import os
import traceback
import json
from IPython.display import display, HTML
import ipywidgets as widgets

import comets
# Global variables
# ----------------
# notebook response file
# dict "previous_responses" is the global variable used to update the file
RESPONSES_FILE = '.questions_responses.json'
if os.path.exists(RESPONSES_FILE):
    with open(RESPONSES_FILE, 'r') as file:
        previous_responses = json.load(file)
else:
    previous_responses = {}

T1Q1 = ("T1Q1", "1", "0")
T1Q2 = ("T1Q2", "3", "0")
T2Q1 = ("T2Q1", "4", "0")
T2Q2 = ("T2Q2", "1", "0")
T3Q1 = ("T3Q1", "2", "0")
T3Q2 = ("T3Q2", "3", "0")
        
def update_response(key, value):
    """Update a response in the json file
    
    The responses file stores previous attempts to answer a question.
    It allows to keep the last answer even if relaunching the notebook kernel.

    Args:
        key (str): question identifier.
        value (str): user answer value.
    """
    previous_responses[key] = value
    with open(RESPONSES_FILE, 'w') as file:
        json.dump(previous_responses, file)
        

# Generic display methods
# -----------------------
def display_score_bar(correct_points, total):
    """
    Displays a score bar for a given exercize
    """
    # Calculate the proportion of errors and correct points
    error_proportion = 1 - (correct_points / total)
    correct_proportion = correct_points / total

    # Define the HTML and CSS for the score bar
    html = f"""
    <div style="width: {correct_proportion*100}%; height: 20px; background-color: #4CAF50; float: left;"></div>
    <div style="width: {error_proportion*100}%; height: 20px; background-color: #f44336; float: left;"></div>
    <p style="clear: both; margin-top: 5px;">Correct Points: {correct_points} / {total}</p>
    """

    # Display the HTML
    display(HTML(html))
    

def question(question):
    """
    """
    response_widgets = {}
    question_text = widgets.Label("Enter the number corresponding to your answer:")
    response = widgets.Text(value=previous_responses.get(question[0], question[2]))
    response.layout.margin = '10px 10px 10px 10px' 
    update_button = widgets.Button(description="Update answer")
    result_label = widgets.Label(value="") # Label for displaying correctness
    result_label.layout.margin = '0px 0px 0px 20px'
    
    def on_button_click(b, response_widget, question, result_label):
        user_response = response_widget.value
        update_response(question[0], response_widget.value)
        correctness = check_answer(question[1], user_response)
        result_label.value = correctness
    
    update_button.on_click(lambda b, response_widget=response, question=question, label=result_label: on_button_click(b, response_widget, question, label))
    
    response_widgets[question] = widgets.VBox([
        question_text,
        response, 
        widgets.HBox([update_button, result_label])
    ])
    
    return widgets.VBox(list(response_widgets.values()))

def check_answer(correct_answer, response):
    if response == correct_answer:
        return "Correct !"
    else:
        return "Incorrect"
    
    
# Exercises
# ---------
def grade_tuto1_ex0():
    global simulator
    points=0
    if isinstance(simulator, comets.CosmoInterface):
        points += 1
        if simulator.simulator_path == 'BreweryTutorialSimulation':
            points += 1
        else:
            print("Hint: Your simulator path is incorrect")
        if simulator.temporary_consumers:
            points += 1
        else:
            print("Hint: Set temporary_consumers to True")  
    else:
        print("Hint: You should create a CosmoInterface object")
  
    # Display score
    total = 3
    display_score_bar(points, total)

def grade_tuto1_ex1(parameter, simulator):

    points = 0
    
    parameter_solution = {
        'Model::{Entity}MyBar::@NbWaiters': 10,
        'Model::{Entity}MyBar::@RestockQty': 12,
    }
    
    # Test parameter
    # --------------
    if parameter == {}:
        print("Fill in the 'parameter' variable.")
    else: 
        if isinstance(parameter, dict):
            if parameter.keys() != parameter_solution.keys():
                print("Hint: one of the provided datapaths is incorrect. Check for typos !")
            if list(parameter.values()) != list(parameter_solution.values()):
                print("Hint: one of the provided attribute value is incorrect. Check for typos !")
            if parameter == parameter_solution:
                points += 1
        else:
            print("Hint: 'parameter' variable should be a python dictionary")
    
    if parameter == parameter_solution:  # Trick to not display hints directly at start.
        if simulator.sim is None:
            print("Your simulator has been destroyed, probably by the command simulator.terminate()"
                  " at the end of the notebook. You need to initialize it again")
        else:
            # Test that simulator values are correct
            # --------------------------------------
            try:
                setted_values = simulator.get_outputs(list(parameter_solution.keys()))
            except Exception as e:
                print("Something is wrong in your simulator object")    
                raise e
            if setted_values != parameter_solution:
                print("Hint: the attribute values are not set in the simulator object.\n"
                    "Use simulator.set_inputs method with the correct argument to set attribute values")
            else:
                points += 1
    # Display score
    total = 2
    display_score_bar(points, total)  


def grade_tuto1_ex2(list_of_outputs, stock, simulator):

    points = 0
    
    list_solution = ['Model::{Entity}MyBar::@Stock']
    
    if simulator.sim is None:
        print("Your simulator has been destroyed, probably by the command simulator.terminate()"
                " at the end of the notebook. You need to initialize it again")
    try:
        stock_solution = simulator.get_outputs(list_solution)
    except Exception as e:
        print("Something is wrong in your simulator object")    
        raise e
    
    # Test list_of_outputs
    # --------------------
    if list_of_outputs == []:
        print("Fill in the 'list_of_output_parameters' variable.")
    else:
        if isinstance(list_of_outputs, list):
            if list_of_outputs != list_solution:
                print("Hint: the provided list in incorrect. Check for typos !")
            else:
                points += 1
        else:
            print("Hint: 'list_of_output_parameters' variable should be a python list")
    
    # Test that simulator values are correct
    # --------------------------------------
    if stock is None:
        print("Fill in the 'stock' variable.")
    else:
        if stock != stock_solution:
            print(f"Hint: variable stock has incorrect value.\n"
                    f"Use simulator.get_outputs method with the correct argument to recover its value.\n"
                    f"You should obtain the following ParameterSet:\n {stock_solution}")
        else:
            points += 1

    # Display score
    total = 2
    display_score_bar(points, total)  
    

def grade_tuto2_ex1(task, output):
    
    points = 0
    
    input_parameter_set = {'NbWaiters': 4, 'RestockQty': 12}
    
    encode_correct = False
    get_outcomes_correct = False
    
    # Cell 1 
    # ------
    
    if not isinstance(task, comets.ModelTask):
        print("Hint: 'mytask2' should be a ModelTask.")
    else:
        if task.encode is None and task.get_outcomes is None:
            print("Fill in the CosmoInterface arguments.")
        else:
            # Check that we still have the correct simulator
            if not task.modelinterface.simulator_path == 'BreweryTutorialSimulation':
                print("Hint: the CosmoInterface provided to the ModelTask does not point towards the correct simulator.")
        
            if task.encode is None:
                print("Hint: you should provide a non-empty 'encode' input argument.")
            else:
                # Encode test
                try:
                    res = task.encode(input_parameter_set)
                except TypeError:
                    print("Hint: the encoder should be a function taking a ParameterSet as positional input argument.")
                else: 
                    if res == {'Model::{Entity}MyBar::@NbWaiters': 4, 'Model::{Entity}MyBar::@RestockQty': 12}:
                        encode_correct = True
                    else:
                        print("Hint: the output of your encode function is incorrect.")
                
            if task.get_outcomes is None:
                print("Hint: you should provide a non-empty 'get_outcomes' input argument.")
                
            
            if task.encode is not None and task.encode is not None:
                # Evaluate() test
                try:
                    res = task.evaluate(input_parameter_set)
                except AttributeError as e:
                    print("An attribute of your input ParameterSet cannot be found in the model. Check your `encode` method.")
                    traceback.print_exc()
                except Exception as e:
                    print("Something is wrong with your Task. Its evaluation raises the following error:")
                    print(e)
                    traceback.print_exc()
                else:
                    if isinstance(res, dict):
                        # Un-ordered equality comparison
                        if set(list(res.keys())) == set(['AverageSatisfaction', 'Stock']):
                            get_outcomes_correct = True
                        else:
                            print("Hint: the output of your get_outcomes function is incorrect."
                                "Provide the get_outcomes function defined earlier in the tutorial.")
                    else:
                        print("Hint: the output of your get_outcomes function should be a dictionary."
                            "Provide the get_outcomes function defined earlier in the tutorial.")

    if encode_correct and get_outcomes_correct:
        points += 1

    # Cell 2 
    # ------
    if output is None:
        print("Fill in the 'output2' variable.")
    else:
        if isinstance(output, dict):
            if set(list(output.keys())) == set(['AverageSatisfaction', 'Stock']):
                points += 1
            else:
                print("Hint: 'output2' does not contain the expected output.")
        else:
            print("Hint: 'output2' should be a dictionary.")
            
    # Display score
    total = 2
    display_score_bar(points, total)  
    
def grade_tuto2_ex2(get_outcomes_func):
    
    points = 0
    
    if not callable(get_outcomes_func):
        print("Hint: 'get_outcomes' should be a python function.")
    else:
        from pathlib import Path
        cwd = Path().resolve()
        simulator = comets.CosmoInterface(
            simulator_path = 'BreweryTutorialSimulation',
            project_path = cwd,
        )
        simulator.initialize()
        try:
            res = get_outcomes_func(simulator)
        except Exception as e:
            print("Something is wrong with your simulator. It is not possible to grade the exercise.")
            raise e
        else:
            if res == { 'maximum capacity percentage' : 0.2}:
                points += 1
            elif res == { 'maximum capacity percentage' : None}:
                print("Fill in the function to assign its value to maximum_capacity_percentage variable.")
            else:
                print(f"The output of your get_outcomes function is incorrect.\n"
                      f"Hint: use get_outputs method of the simulator to get the Stock value, then divide it by 50.")
                
    # Display score
    total = 1
    display_score_bar(points, total)  