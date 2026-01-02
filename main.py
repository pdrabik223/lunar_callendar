from pi_pico_w_server_tools.app import App , compose_response, load_html
import socket

app = App(hostname="lunar_calendar.local")

def home_page(cl: socket.socket, parameters: dict):    
    cl.sendall(compose_response(response=load_html("static/index.html")))


if __name__ == "__main__":
    
    app.register_endpoint("/v1", home_page)
    
    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print(f"Server error type: {type(ex)}\tmessage: {ex}\texiting")