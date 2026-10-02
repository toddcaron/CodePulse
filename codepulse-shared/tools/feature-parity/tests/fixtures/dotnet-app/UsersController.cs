using Microsoft.AspNetCore.Mvc;

public class UsersController : ControllerBase
{
    [HttpPost("users")]
    public IActionResult CreateUser() => Ok();
}